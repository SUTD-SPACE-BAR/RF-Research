---
title: Matrices and linear algebra for networks, arrays and calibration
domain: 00-math-foundations
slug: matrices-and-linear-algebra-for-networks
tags: [linear-algebra, nodal-analysis, mna, eigenvalues, network-matrices, z-parameters, y-parameters, s-parameters, abcd, svd, mimo, beamforming, least-squares, calibration, conditioning]
prerequisites: [complex-numbers-and-phasors.md]
related:
  - numerical-methods-overview.md
  - differential-equations-circuits-waves.md
  - ../01-circuit-theory/two-port-networks-zyh-abcd.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../03-transmission-lines-matching/signal-flow-graphs-mason.md
  - ../12-phased-arrays/adaptive-beamforming-doa.md
  - ../12-phased-arrays/array-calibration.md
  - ../11-radar/mimo-radar-virtual-arrays.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
  - ../16-simulation-tools/spice-circuit-simulation.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Matrices and linear algebra for networks, arrays and calibration

## Questions this page answers
- How does a circuit simulator actually solve a circuit (nodal analysis, MNA)?
- What do Z, Y, ABCD and S matrices mean, and how do I convert between them?
- Why is a reciprocal network's S-matrix symmetric, and a lossless one's unitary?
- What do eigenvalues tell me about a circuit (natural frequencies, coupled resonators)?
- Why does MIMO capacity involve the singular value decomposition?
- How do adaptive beamformers use covariance matrices and eigenvectors?
- How does VNA calibration become a linear-equation solve?
- What is least squares, and why do calibration fits go numerically wrong (conditioning)?

## TL;DR
- Linear circuits in phasor form are linear equations: **nodal analysis** $\mathbf Y\mathbf V=\mathbf I$ (admittance matrix × node voltages = injected currents). **MNA** adds rows for voltage sources/inductors so any circuit can be written $\mathbf A\mathbf x=\mathbf b$ — that's what SPICE solves at every frequency (`.ac`) and every Newton/time step (`.op`, `.tran`).
- Multiport **network matrices** relate port quantities: $\mathbf V=\mathbf Z\mathbf I$, $\mathbf I=\mathbf Y\mathbf V$, cascade $\begin{bmatrix}V_1\\I_1\end{bmatrix}=\mathbf{ABCD}\begin{bmatrix}V_2\\I_2\end{bmatrix}$, waves $\mathbf b=\mathbf S\mathbf a$. With equal real reference $Z_0$: $\mathbf S=(\mathbf Z-Z_0\mathbf I)(\mathbf Z+Z_0\mathbf I)^{-1}$.
- Reciprocal ⇒ $\mathbf Z=\mathbf Z^T$, $\mathbf S=\mathbf S^T$. Lossless ⇒ $\mathbf S^H\mathbf S=\mathbf I$ (unitary). Passive ⇒ eigenvalues of $\mathbf I-\mathbf S^H\mathbf S$ ≥ 0. Cascades multiply ABCD (or T) matrices.
- **Eigenvalues** of a state matrix are the poles; two identical resonators coupled by $k$ split into $f_0/\sqrt{1\pm k}$ (splitting ≈ $kf_0$) — the basis of coupled-resonator filter design.
- **SVD** $\mathbf H=\mathbf U\boldsymbol\Sigma\mathbf V^H$ turns a MIMO channel into parallel independent channels with gains $\sigma_i$: $C=\sum\log_2(1+\frac{\mathrm{SNR}}{N_t}\sigma_i^2)$. A rank-1 (pure LOS, closely spaced) channel gives array gain but no multiplexing.
- **Covariance eigen-decomposition** separates signal and noise subspaces (MUSIC); **MVDR** weights $\mathbf w\propto\mathbf R^{-1}\mathbf a$ keep unit gain on the look direction and null strong interferers.
- **Least squares** $\min\|\mathbf A\mathbf x-\mathbf b\|^2$ (solve with QR/`lstsq`, not normal equations) fits calibrations: the 3-term VNA one-port error model is linear in $(e_{00},e_{11},\Delta_e)$ and is solved exactly by open/short/load. Centre and scale variables before polynomial fits: a cubic fit in raw kelvin has condition number ~10¹⁰ vs ~6 when scaled.

## Intuition (no math)
A matrix is a bookkeeping device for "many linear relationships at once". In a circuit, every node's current balance depends linearly on its neighbours' voltages; writing all of those balances together gives one matrix equation. Solving it is like solving simultaneous equations at school, just with more unknowns (and complex numbers at AC).

Network matrices describe a black box by how its ports respond. The S-matrix is the most natural at RF: "if I send a wave into port 1, how much comes back out of port 1 (reflection) and out of port 2 (transmission)?" Because a passive box can't create energy, the outgoing waves can't carry more power than the incoming ones — which becomes a clean matrix condition.

Eigenvalues are a system's "natural settings" — the frequencies at which it likes to ring, the directions in which a matrix just stretches without rotating. Two identical tuned circuits placed near each other stop ringing at one frequency and ring at two slightly different ones: the in-phase and out-of-phase modes. That splitting is what sets a bandpass filter's bandwidth.

SVD says any linear map is "rotate, stretch along perpendicular axes, rotate". For a MIMO radio link, that means the tangled multi-antenna channel is secretly a set of independent parallel pipes, each with its own gain. Use them all and capacity multiplies.

Least squares: when you have more measurements than unknowns and every measurement is a bit noisy, pick the answer that minimises the total squared error. It's how you fit a calibration curve, a magnetometer ellipsoid, or VNA error terms.

## The math

### Level 1 — simultaneous equations and matrix notation

A set of linear equations
$$\begin{aligned}a_{11}x_1+a_{12}x_2&=b_1\\a_{21}x_1+a_{22}x_2&=b_2\end{aligned}\quad\Longleftrightarrow\quad\mathbf A\mathbf x=\mathbf b,\qquad\mathbf x=\mathbf A^{-1}\mathbf b.$$
For 2×2: $\mathbf A^{-1}=\frac{1}{a_{11}a_{22}-a_{12}a_{21}}\begin{bmatrix}a_{22}&-a_{12}\\-a_{21}&a_{11}\end{bmatrix}$ — invertible iff the determinant is non-zero. Matrix product $(\mathbf{AB})_{ij}=\sum_ka_{ik}b_{kj}$; order matters ($\mathbf{AB}\ne\mathbf{BA}$ in general). Transpose $\mathbf A^T$ swaps rows and columns; conjugate transpose (Hermitian) $\mathbf A^H=(\mathbf A^*)^T$.

**Nodal analysis by inspection** (no voltage sources): diagonal $Y_{ii}$ = sum of admittances connected to node $i$; off-diagonal $Y_{ij}$ = −(admittance between $i$ and $j$); right side = currents injected into each node. Example (verified): 1 mA into node 1; 1 kΩ from node 1 to ground, 2 kΩ between nodes, 3 kΩ from node 2 to ground → $V_1=0.833$ V, $V_2=0.5$ V. Networks of R, L, C (no dependent sources) give **symmetric** $\mathbf Y$ — reciprocity.

### Level 2 — MNA, network matrices, eigenvalues

**Modified nodal analysis (MNA)** [1]. Voltage sources and inductors (at DC) don't fit $\mathbf Y\mathbf V=\mathbf I$ because their current isn't a function of voltage. MNA adds each such branch current as an extra unknown and its constitutive equation as an extra row:
$$\begin{bmatrix}\mathbf G&\mathbf B\\\mathbf C&\mathbf D\end{bmatrix}\begin{bmatrix}\mathbf v\\\mathbf j\end{bmatrix}=\begin{bmatrix}\mathbf i\\\mathbf e\end{bmatrix}.$$
Example (verified): 5 V source, two 1 kΩ in series → node 2 at 2.5 V, source branch current −2.5 mA (SPICE sign convention: current into the + terminal). At AC the entries are complex admittances $j\omega C$, $1/(j\omega L)$. Nonlinear devices are linearised each Newton iteration (companion models), and `.tran` turns capacitors/inductors into conductances plus history sources each time step — so every SPICE run is a long sequence of sparse $\mathbf A\mathbf x=\mathbf b$ solves ([SPICE](../16-simulation-tools/spice-circuit-simulation.md), [numerical methods](numerical-methods-overview.md)).

**AC nodal example — an L-match (verified).** Match $R_L=10$ Ω to 50 Ω at 433 MHz with series L and shunt C (C on the 50 Ω side): $Q=\sqrt{50/10-1}=2$, $X_L=QR_L=20$ Ω → 7.35 nH, $X_C=50/Q=25$ Ω → 14.70 pF. Build the 2-node complex $\mathbf Y$, invert, read $Z_{\rm in}=(\mathbf Y^{-1})_{11}=50.000+j0$ Ω. ([impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).

**Network matrices** [2 §4.1–4.4]. For an $N$-port with port voltages $\mathbf V$ and currents $\mathbf I$ (into the ports):

| Matrix | Definition | Measured with | Cascading / use |
|---|---|---|---|
| $\mathbf Z$ | $\mathbf V=\mathbf Z\mathbf I$ | other ports open | series connections add Z |
| $\mathbf Y$ | $\mathbf I=\mathbf Y\mathbf V$ | other ports shorted | parallel connections add Y |
| ABCD (2-port) | $V_1=AV_2+BI_2$, $I_1=CV_2+DI_2$ ($I_2$ out of port 2) | — | cascades **multiply** |
| $\mathbf S$ | $\mathbf b=\mathbf S\mathbf a$, $a_i=\frac{V_i^++}{\sqrt{Z_0}}$… (incident/reflected power waves) | other ports matched | what a VNA measures |
| T (transfer scattering) | $[b_1,a_1]^T=\mathbf T[a_2,b_2]^T$ | — | cascades multiply (S-domain) |

With incident/reflected voltage waves $V^\pm$ and $a=V^+/\sqrt{Z_0}$, $b=V^-/\sqrt{Z_0}$, $V=V^++V^-$, $I=(V^+-V^-)/Z_0$, one finds (equal real $Z_0$ at all ports)
$$\mathbf S=(\mathbf Z-Z_0\mathbf I)(\mathbf Z+Z_0\mathbf I)^{-1},\qquad\mathbf Z=Z_0(\mathbf I+\mathbf S)(\mathbf I-\mathbf S)^{-1}$$
— the matrix generalisation of $\Gamma=(Z-Z_0)/(Z+Z_0)$. Verified against scikit-rf's `z2s`. Full conversion tables (including ABCD) are in Pozar's two-port conversion table (§4.4; numbered Table 4.2 as recalled) [2] and on [two-port networks](../01-circuit-theory/two-port-networks-zyh-abcd.md) / [S-parameters](../03-transmission-lines-matching/s-parameters.md).

**Structural properties** (verified for a lossless and a lossy T-network) [2 §4.3]:
- Reciprocal (no ferrites/active devices/magnetised plasma): $\mathbf Z=\mathbf Z^T$, $\mathbf Y=\mathbf Y^T$, $\mathbf S=\mathbf S^T$; for ABCD, $AD-BC=1$.
- Lossless: $\mathbf S^H\mathbf S=\mathbf I$ — columns are orthonormal: $|S_{11}|^2+|S_{21}|^2=1$ and $S_{11}^*S_{12}+S_{21}^*S_{22}=0$. Consequence: a lossless reciprocal 3-port cannot be matched at all ports (why Wilkinson dividers need a resistor, and circulators need non-reciprocity).
- Passive: $\mathbf I-\mathbf S^H\mathbf S$ positive semidefinite (its eigenvalues are the fractions of power dissipated for each input "direction"). Measured S-parameter files that violate this (from noise or bad de-embedding) make time-domain simulations blow up — hence "passivity enforcement".

**Eigenvalues and eigenvectors.** $\mathbf A\mathbf v=\lambda\mathbf v$: directions $\mathbf v$ that $\mathbf A$ only scales. Found from $\det(\mathbf A-\lambda\mathbf I)=0$ [3 ch. 6].
- *State-space*: for $\dot{\mathbf x}=\mathbf A\mathbf x$, eigenvalues of $\mathbf A$ are the natural frequencies (poles). Series RLC with $\mathbf x=[v_C,i_L]$: $\mathbf A=\begin{bmatrix}0&1/C\\-1/L&-R/L\end{bmatrix}$ — eigenvalues equal the roots of $LCs^2+RCs+1$ (verified).
- *Coupled resonators*: two identical LC tanks with mutual inductance $M=kL$ obey $\omega^2\mathbf L\mathbf i=\mathbf C^{-1}\mathbf i$ with $\mathbf L=\begin{bmatrix}L&M\\M&L\end{bmatrix}$ — a generalised eigenproblem. Eigenvectors: in-phase $[1,1]$ at $\omega_0/\sqrt{1+k}$ and anti-phase $[1,-1]$ at $\omega_0/\sqrt{1-k}$ (verified at 433 MHz, k = 0.05: 422.7 and 444.4 MHz). Splitting ≈ $kf_0$ is how coupling coefficients are extracted from EM simulations of filter resonators ([RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).
- *Stability*: a linear system is stable iff all eigenvalues of its state matrix have negative real parts.

### Level 3 — SVD, arrays, least squares, conditioning

**Singular value decomposition.** Any complex $m\times n$ matrix factors as $\mathbf H=\mathbf U\boldsymbol\Sigma\mathbf V^H$ with unitary $\mathbf U,\mathbf V$ and non-negative diagonal $\boldsymbol\Sigma$ ($\sigma_1\ge\sigma_2\ge\dots$) [3 ch. 7]. Rank = number of non-zero $\sigma_i$. $\|\mathbf H\|_2=\sigma_1$; condition number $\kappa=\sigma_1/\sigma_{\min}$.

**MIMO capacity** [4 §7.1]. For $\mathbf y=\mathbf H\mathbf x+\mathbf n$ with $N_t$ transmit antennas, precoding with $\mathbf V$ and combining with $\mathbf U^H$ gives independent scalar channels $\tilde y_i=\sigma_i\tilde x_i+\tilde n_i$. With equal power per antenna:
Full MIMO treatment (water-filling derivation, diversity, Alamouti, channel estimation): [MIMO page](../10-comms-modulation/mimo-capacity-and-channel-estimation.md).
$$C=\sum_i\log_2\!\left(1+\frac{\mathrm{SNR}}{N_t}\sigma_i^2\right)=\log_2\det\!\left(\mathbf I+\frac{\mathrm{SNR}}{N_t}\mathbf H\mathbf H^H\right)\ \text{b/s/Hz}.$$
Water-filling power allocation over the $\sigma_i$ does at least as well (verified). A **rank-1** channel (all antennas see one dominant path, e.g. a rocket far away in clear LOS with closely spaced antennas) has one non-zero singular value: you get array gain ($\sigma_1^2=N_tN_r$) but no spatial multiplexing (verified: 2×2 all-ones channel at 20 dB SNR gives 7.65 b/s/Hz vs 8.48 for a random rich-scattering draw).

**Array signal processing** ([adaptive beamforming](../12-phased-arrays/adaptive-beamforming-doa.md)). For an $N$-element array with steering vector $\mathbf a(\theta)$ (element phases $e^{jkd n\sin\theta}$), the spatial covariance is $\mathbf R=E[\mathbf x\mathbf x^H]=\sum_kP_k\mathbf a_k\mathbf a_k^H+\sigma^2\mathbf I$.
- Eigen-decomposition: $D$ sources give $D$ large eigenvalues (signal subspace); the other $N-D$ equal $\sigma^2$ (noise subspace). MUSIC scans $\mathbf a(\theta)$ for directions orthogonal to the noise subspace. Verified: one 20 dB source on 8 elements gives $\lambda_1=100\cdot8+1=801$ and the rest exactly 1.
- **MVDR/Capon**: $\mathbf w=\dfrac{\mathbf R^{-1}\mathbf a_0}{\mathbf a_0^H\mathbf R^{-1}\mathbf a_0}$ — unit gain towards $\theta_0$, minimum output power otherwise, so strong interferers are nulled (verified: an interferer 20 dB above noise at 30° is suppressed by > 35 dB).
- **Array calibration** — gain/phase errors per element are estimated by least squares against known sources ([array calibration](../12-phased-arrays/array-calibration.md)).

**Least squares** [3 ch. 4]. For an overdetermined $\mathbf A\mathbf x\approx\mathbf b$ (more equations than unknowns), minimise $\|\mathbf A\mathbf x-\mathbf b\|_2^2$. Solution: normal equations $\mathbf A^H\mathbf A\mathbf x=\mathbf A^H\mathbf b$, but compute it via QR or SVD (`numpy.linalg.lstsq`) because forming $\mathbf A^H\mathbf A$ squares the condition number. Weighted LS: scale each row by $1/\sigma_i$ (measurement uncertainty). Regularised (ridge): add $\lambda\|\mathbf x\|^2$ when the problem is ill-conditioned.

**VNA one-port calibration as linear algebra.** The 3-term error model relates measured $\Gamma_m$ to actual $\Gamma_a$: $\Gamma_m=e_{00}+\dfrac{e_{01}e_{10}\Gamma_a}{1-e_{11}\Gamma_a}$. Multiply out:
$$\Gamma_m=e_{00}+\Gamma_a\Gamma_m\,e_{11}-\Gamma_a\,\Delta_e,\qquad\Delta_e=e_{00}e_{11}-e_{01}e_{10}$$
— linear in the unknowns $(e_{00},e_{11},\Delta_e)$. Three known standards (open Γ = 1, short −1, load 0) give a 3×3 complex system; more standards give a least-squares fit. Then correct a DUT with $\Gamma_a=\dfrac{\Gamma_m-e_{00}}{e_{11}(\Gamma_m-e_{00})+e_{01}e_{10}}$. Verified: exact recovery with ideal OSL, and < 3×10⁻³ error with five noisy standards [5] ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md), [NanoVNA](../17-test-measurement/nanovna-librevna-practical.md)). (Real cal kits use non-ideal, frequency-dependent standard models.)

**Conditioning.** Relative error in $\mathbf x$ can be up to $\kappa(\mathbf A)$ × relative error in $\mathbf b$. Polynomial fits in raw units are notoriously ill-conditioned: fitting a crystal's frequency–temperature cubic with $T$ in kelvin gives $\kappa\approx3.7\times10^{10}$; centring and scaling $T$ gives $\kappa\approx6$ (verified). Same lesson for magnetometer/IMU calibration fits (the Space Bar calibration notes stress fit guards) and for Touchstone de-embedding with nearly singular fixtures.

**Other decompositions you'll meet.** LU (sparse circuit solves), Cholesky (Hermitian positive-definite, e.g. covariance), QR (least squares, Gram–Schmidt), eigen-decomposition of Hermitian matrices (real eigenvalues, orthogonal eigenvectors — noise correlation matrices, power), Kronecker products (planar arrays: $\mathbf a_{xy}=\mathbf a_x\otimes\mathbf a_y$; MIMO radar virtual arrays).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $\mathbf Y\mathbf V=\mathbf I$; MNA $\mathbf A\mathbf x=\mathbf b$ | linear(ised) circuits | SPICE core |
| $\mathbf S=(\mathbf Z-Z_0\mathbf I)(\mathbf Z+Z_0\mathbf I)^{-1}$ | equal real $Z_0$ | |
| $\mathbf S=\mathbf S^T$ / $\mathbf S^H\mathbf S=\mathbf I$ | reciprocal / lossless | $\lvert S_{11}\rvert^2+\lvert S_{21}\rvert^2=1$ |
| ABCD$_{\rm total}$ = ABCD₁·ABCD₂ | cascade | |
| $AD-BC=1$ | reciprocal 2-port | |
| $f_\pm=f_0/\sqrt{1\mp k}$ | two identical coupled resonators | k = 0.05 @ 433 MHz → 22 MHz split |
| $C=\sum\log_2(1+\frac{\rm SNR}{N_t}\sigma_i^2)$ | MIMO, CSI at Rx, equal power | |
| $\mathbf w\propto\mathbf R^{-1}\mathbf a_0$ | MVDR | |
| use `lstsq`/QR, centre & scale | least squares | κ 10¹⁰ → 6 |

## Worked examples

**1. SPICE-style solve of a bias network.** A 3.3 V rail, 10 kΩ/4.7 kΩ divider with a 100 kΩ load on the tap: MNA unknowns [V₁, V₂, I_src]; solving gives V₂ = 3.3 × (4.7‖100)/(10 + 4.7‖100) = 1.02 V. The same matrix with complex entries gives the AC response of the divider plus decoupling cap.

**2. L-match at 433 MHz** (verified): 10 Ω PA-style load to 50 Ω with 7.35 nH series + 14.70 pF shunt; $Z_{\rm in}=50$ Ω exactly at 433 MHz. Sweeping frequency in the same matrix shows the match bandwidth: return loss > 10 dB from 343 to 507 MHz and > 20 dB from 408 to 457 MHz (computed by the same nodal solve).

**3. Is my measured 2-port passive?** A NanoVNA 2-port file of an attenuator at one frequency gives $\mathbf S=\begin{bmatrix}0.05&0.50\\0.50&0.05\end{bmatrix}$: $\mathbf S^H\mathbf S$ has eigenvalues $(0.05\pm0.5)^2$ = 0.3025 and 0.2025, so $\mathbf I-\mathbf S^H\mathbf S$ has eigenvalues 0.70, 0.80 ≥ 0 — passive (≈ 6 dB pad). A file where an eigenvalue of $\mathbf S^H\mathbf S$ exceeds 1 is non-physical (calibration error or noise at high loss).

**4. Coupled-resonator bandpass at 433 MHz.** Two resonators (10 nH, 13.5 pF) with coupling k = 0.05 show two peaks at 422.7 and 444.4 MHz when lightly loaded; for a 2-pole Butterworth response with fractional bandwidth $w$, the required coupling is $k=w/\sqrt{g_1g_2}=w/\sqrt2$ (from the filter-prototype $g$ values; see [filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)): a 10 MHz bandwidth (w = 2.3 %) needs k ≈ 0.016.

**5. MIMO on a rocket?** Two antennas on the rocket and two at the ground station 10 km away with 1 m separation: the channel is essentially rank-1 (the angular spread seen from the ground is tiny), so MIMO multiplexing gives nothing; use the second antenna for diversity (against airframe nulls and polarisation rotation) or combining gain (+3 dB).

**6. Magnetometer / sensor calibration fit.** Fitting hard/soft-iron ellipsoid parameters is a least-squares problem with 9–10 unknowns; always centre/scale the raw counts, use `lstsq`, check the condition number and residuals, and (per the Space Bar calibration notes) remember that fits cannot see axis-permutation errors — a separate dip-angle test is needed.

## Practical notes
- `numpy.linalg.solve` (never `inv(A) @ b`), `lstsq`, `svd`, `eig`/`eigh` (Hermitian), `cond`; `scipy.linalg.lu`, `qr`, `cholesky`; `scipy.sparse.linalg.spsolve` for big circuits/FEM.
- scikit-rf: `Network.s`, `.z`, `.y`, `.a`; conversions `skrf.network.z2s`, `s2z`, etc.; cascading with `**`; `Network.is_passive()`-style checks can be built from `S^H S`.
- Port conventions differ: ABCD uses $I_2$ *out of* port 2; Z/Y use currents *into* ports. Mixing them flips signs of $C$ and $D$.
- Complex vs real transpose: in numpy `A.T` is the plain transpose; use `A.conj().T` for Hermitian.

## Common mistakes & misconceptions
1. **Inverting matrices to solve systems** — slower and less accurate than `solve`/LU.
2. **Using $\mathbf A^T$ where $\mathbf A^H$ is needed** — breaks power/lossless checks and beamformer formulas.
3. **Assuming S is symmetric for any network** — only reciprocal ones; amplifiers, isolators, circulators are not.
4. **Normal equations for ill-conditioned fits** — square the condition number; use QR.
5. **Forgetting reference impedance** — S-parameters are meaningless without $Z_0$ (and can be complex-referenced — "power waves" vs "pseudo-waves" definitions differ; see [S-parameters](../03-transmission-lines-matching/s-parameters.md)).
6. **Expecting MIMO gains in LOS long-range links** — rank limits multiplexing.
7. **Treating eigenvalues of S as reflection coefficients of ports** — they're reflection coefficients of eigen-excitations (useful for antennas arrays' "active reflection" analysis), not of individual ports.
8. **Ignoring ABCD current sign convention** when cascading measured data.

## How to simulate / verify
- `python3 tools/verify/math_matrices.py` — DC nodal and MNA; 433 MHz L-match by complex nodal analysis; Z→S vs scikit-rf; reciprocity/losslessness/passivity; ABCD cascade vs scikit-rf; coupled-resonator eigenfrequencies; state-space poles; MIMO capacity (SVD = log-det, water-filling, rank-1); MVDR null and covariance eigenvalues; OSL VNA calibration (exact and least squares) and DUT correction; polynomial-fit conditioning. All PASS.

## Open questions / gaps
- Mixed-mode (differential) S-parameters and the associated transformation matrices belong to 03-transmission-lines-matching / 13-pcb.
- 8- and 12-term two-port VNA error models (SOLT, TRL) extend the one-port example; 17-test-measurement should show their linear-algebra formulation.

## Sources
1. C.-W. Ho, A. E. Ruehli, P. A. Brennan, "The modified nodal approach to network analysis," *IEEE Trans. Circuits and Systems* 22(6):504–509 (1975), doi:10.1109/TCS.1975.1084079. https://web.engr.oregonstate.edu/~karti/ece521/mna.pdf (peer-reviewed).
2. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley (2012): §4.2 impedance and admittance matrices (reciprocal/lossless properties), §4.3 scattering matrix (unitary property for lossless networks), §4.4 ABCD matrix, conversion table (Table 4.2 as recalled — table number not verified) (textbook; section numbers checked by W5-S18 (2026-10-13) against the Wiley 4th-ed. ToC transcribed in gaps/D4-curriculum.md §3.1; corrected §4.1 → §4.2, since §4.1 is equivalent voltages and currents for waveguide modes).
3. G. Strang, *Introduction to Linear Algebra*, 5th ed., Wellesley-Cambridge (2016): ch. 2 (elimination, LU), ch. 4 (orthogonality, least squares, QR), ch. 6 (eigenvalues), ch. 7 (SVD); MIT 18.06 lecture notes https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/ (textbook/lecture notes).
4. D. Tse, P. Viswanath, *Fundamentals of Wireless Communication*, Cambridge (2005), ch. 7 "MIMO I: spatial multiplexing and channel modeling" (§7.1 capacity via SVD). https://web.stanford.edu/~dntse/papers/book121004.pdf (textbook, free draft).
5. Keysight Technologies, *Applying Error Correction to Network Analyzer Measurements*, AN 1287-3 (one-port 3-term error model) — standard reference for the OSL model re-derived here (app note; not re-read this session).
6. H. L. Van Trees, *Optimum Array Processing*, Wiley (2002), ch. 6 (MVDR/Capon), ch. 9 (subspace methods incl. MUSIC) (textbook; cited for standard results verified numerically).
