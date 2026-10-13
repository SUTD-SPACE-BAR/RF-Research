---
title: Couplers, power dividers and combiners (Wilkinson, branch-line, rat-race, Lange, coupled-line, resistive)
domain: 06-rf-circuits
slug: couplers-dividers-combiners
tags: [wilkinson, power-divider, combiner, hybrid, branch-line, quadrature-hybrid, rat-race, 180-hybrid, lange, directional-coupler, coupled-line, directivity, isolation, resistive-splitter, combining-efficiency, even-odd-mode]
prerequisites:
  - ../03-transmission-lines-matching/input-impedance-stubs-quarter-wave.md
  - ../03-transmission-lines-matching/s-parameters.md
  - ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md
related:
  - baluns-and-rf-transformers.md
  - power-amplifiers.md
  - lna-design.md
  - detectors-and-power-meters.md
  - mixers.md
  - rf-filters-lc-saw-baw-cavity-microstrip.md
  - ../08-antennas/antenna-polarization-and-circular-polarization.md
  - ../08-antennas/patch-antennas.md
  - ../12-phased-arrays/beamforming-architectures.md
  - ../17-test-measurement/vna-fundamentals-calibration.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Couplers, power dividers and combiners

## Questions this page answers
- How does a Wilkinson divider work, and why does it need a resistor between the outputs?
- Why can't a three-port be lossless, matched and reciprocal at the same time?
- How do I design a Wilkinson for 2.45 GHz in microstrip, or with lumped L and C at 433 MHz?
- How do I make an unequal (e.g. 2:1) power split?
- What are branch-line (90°) and rat-race (180°) hybrids used for?
- How do I feed a circularly polarised GNSS patch with a quadrature hybrid, and how good will the axial ratio be?
- What are coupling, directivity and isolation, and why is my microstrip coupler's directivity so poor?
- How do I sample a PA's output power with a directional coupler?
- What is a Lange coupler?
- When should I use a resistive splitter instead?
- How much power do I lose when combining two PAs that are not perfectly in phase — or when one fails?
- If the Wilkinson's lines are lossy, what resistor gives the best isolation?
- What happens if the two outputs see different loads, or are tied together into 25 Ω or 50 Ω?
- What happens when I combine two *uncorrelated* signals or noise sources in a Wilkinson? Does the resistor waste half?
- Does a Wilkinson combiner protect my PAs from a bad antenna?
- How does a Mini-Circuits-style transformer splitter work, and what sets its frequency range?
- What is a 180° hybrid transformer, and how is it related to the 0° splitter's resistor?
- Should a transmission-line-transformer hybrid be wound as a 25, 50 or 100 Ω pair, and how long can it be?
- How do I feed several receivers from one antenna without losing sensitivity (multicoupler)?
- Which splitter covers several octaves?

## TL;DR
- **A lossless, reciprocal, matched three-port is impossible** (unitarity forbids it). A T-junction is lossless but unmatched/unisolated; the **Wilkinson** adds a resistor $R=2Z_0$ between outputs that carries no current in normal (even-mode) operation but absorbs odd-mode (mismatch/imbalance) power, giving match at all ports and output isolation. Arms are λ/4 of $\sqrt2Z_0=70.7\ \Omega$; $S_{21}=S_{31}=-j/\sqrt2$ (verified).
- Single-section Wilkinson: RL and isolation > 20 dB over ≈ 36 % bandwidth (2.01–2.89 GHz for $f_0$ = 2.45 GHz). On 0.8 mm FR-4, 70.7 Ω = 0.81 mm wide, λ/4 = 17.2 mm. **Lumped** version at 433.92 MHz: L = 25.9 nH, C = 5.19 pF (10.4 pF at the common node), R = 100 Ω; 20 dB bandwidth 394–466 MHz (17 %).
- **Unequal split** $P_3/P_2=K^2$: $Z_{03}=Z_0\sqrt{(1+K^2)/K^3}$, $Z_{02}=K^2Z_{03}$, $R=Z_0(K+1/K)$, outputs at $Z_0K$ and $Z_0/K$ (then transform to 50 Ω). For 2:1: 51.5 Ω, 103 Ω, 106 Ω; verified exactly.
- **Branch-line (quadrature) hybrid**: four λ/4 lines, 35.4 Ω and 50 Ω; outputs −3 dB at 0° and −90° (relative), 4th port isolated. At 1575.42 MHz, over 1559–1610 MHz: amplitude balance within 0.03 dB, phase 90.00–90.01°, RL/isolation ≥ 27.6 dB — an ideal dual-fed RHCP patch would keep axial ratio < 0.03 dB from the hybrid alone.
- **Rat-race (180°) hybrid**: 1.5 λ ring of 70.7 Ω; one input splits in phase, the other in anti-phase, and they are mutually isolated — the basis of balanced mixers, sum/difference (monopulse) networks and baluns.
- **Coupled-line coupler**: $C=\frac{Z_{0e}-Z_{0o}}{Z_{0e}+Z_{0o}}$, $Z_0=\sqrt{Z_{0e}Z_{0o}}$ (10 dB: 69.4/36.0 Ω; 20 dB: 55.3/45.2 Ω). Ideal TEM: infinite directivity. **Microstrip**: unequal even/odd velocities give only ≈ 11 dB directivity (10 dB coupler) and ≈ 6 dB (20 dB coupler) on FR-4 — use stripline, compensation, or a bought coupler when you need to measure reflected power.
- **Resistive star splitter** ($Z_0/3$ each): matched, −6 dB each way, only 6 dB output-to-output isolation, very broadband — fine for test setups and LO distribution, not for combining PAs.
- **Combining efficiency** of two equal sources with phase error Δφ is $\cos^2(\Delta\varphi/2)$ (30° → 93 %, 90° → 50 %); amplitude imbalance of 3 dB still gives 97 %. If one of N PAs dies, output falls to $(N-1)^2/N^2$ (N = 2: −6 dB; N = 8: −1.2 dB) and the difference heats the isolation resistors.

- **Non-ideal Wilkinson** (verified by `rf2_wilkinson_nonideal.py`):
  - With lossy arms (loss αl Np each) the best-isolation resistor is $R_{opt}\approx2Z_0(1+\sqrt2\,\alpha l)$: 104 Ω for 0.25 dB arms, against 40 dB isolation with 100 Ω. Unequal loads give exactly $\Gamma_{in}=-(\Gamma_2+\Gamma_3)/2$.
  - Outputs tied into 25 Ω match perfectly; tied into 50 Ω, $S_{11}=-1/3$.
  - **Uncorrelated** equal inputs deliver P, not 2P, with P lost in the resistor. The resistor's own noise never reaches the input port ($C_{11}=0$).
  - A combiner does **not** protect PAs from a bad antenna: the reflection returns to both PAs in even mode.
- **Broadband transformer hybrids** (verified by `s15_tlt_splitter.py`): the 0° splitter is a centre-tapped hybrid + 100 Ω + a 50→25 Ω transformer, i.e. a lumped Wilkinson. The low edge is set by winding inductance ($2\pi f_L\,4L_{half}\approx2\times100\ \Omega$) and the top edge by line length: wind the pair as **≈ 50 Ω** and expect $f_{hi}\approx0.06/t_d$ (line ≈ 21°). A Δ winding turns the same core into a 180° hybrid, and its termination replaces the resistor.
- **Multicoupler:** 4 receivers on one antenna: passive split NF 12.5 dB → 1.5 dB with a 20 dB / 1 dB LNA in front (but IIP3 −24 dBm), so pick a high-OIP3 amplifier with just enough gain.

## Intuition (no math)
Split a transmission line into two with a simple T and each branch sees the other in parallel: 25 Ω instead of 50 Ω. Quarter-wave transformers of 70.7 Ω can fix the input match, but now the two outputs are directly connected through the junction: power reflected from one output goes straight into the other. That is the job of the Wilkinson's resistor. When both outputs are driven symmetrically (normal division), the two ends of the resistor are at the same voltage — no current, no loss. When something unsymmetrical happens (one port mismatched, or two unequal signals combined), the antisymmetric part of the wave sees the resistor and is absorbed, so it never reaches the other port. Even/odd-mode analysis is simply the mathematical version of "split any excitation into a symmetric part and an antisymmetric part and analyse each separately".

A 90° hybrid is a little ring of four quarter-wave lines. Waves travelling the two ways around the ring arrive at one output in phase (they add), at another with a 90° difference, and at the fourth port 180° apart (they cancel — isolation). A 180° rat-race does the same with a longer ring so that the cancellation pattern gives sum and difference outputs. A coupled-line coupler lets two parallel lines "leak" a sample of the wave from one to the other; the sampled wave in an ideal coupler travels *backwards*, so it separates forward from reflected power — that direction-sensing is its whole value.

## The math

### Level 1 — definitions
For a four-port directional coupler (1 input, 2 through, 3 coupled, 4 isolated), with $P_i$ powers:
$$\text{Coupling } C=10\log\frac{P_1}{P_3},\quad \text{Directivity } D=10\log\frac{P_3}{P_4},\quad \text{Isolation } I=10\log\frac{P_1}{P_4}=C+D,\quad \text{Insertion loss}=10\log\frac{P_1}{P_2}.$$
A quadrature (90°) or 180° hybrid is a 3 dB coupler. A power divider is a three-port (or N+1 port) whose outputs receive given fractions of the input.

### Level 2 — derivations

**(a) No lossless matched reciprocal three-port.** If all ports are matched ($S_{ii}=0$) and the network is reciprocal, $S=\begin{bmatrix}0&a&b\\a&0&c\\b&c&0\end{bmatrix}$. Losslessness requires $S^HS=I$: $|a|^2+|b|^2=1$, $|a|^2+|c|^2=1$, $|b|^2+|c|^2=1$ **and** $b^*c=0$, $a^*c=0$, $a^*b=0$. The last three force two of $a,b,c$ to be zero, contradicting the first three. So a divider must give up one of: lossless (Wilkinson — its resistor), matched at all ports (T-junction), or reciprocal (circulator) [1 §7.1].

**(b) Wilkinson by even/odd modes** [1 §7.3]. Normalise $Z_0=1$; draw the divider symmetrically with ports 2 and 3 at the outputs, arm impedance $Z$, resistor $r$ between the outputs split as $r/2$ to the symmetry plane.
- *Even mode* (ports 2 and 3 driven equally): no current crosses the symmetry plane → open circuit there; the resistor halves float. Each half is a λ/4 line of impedance $Z$ feeding port 1's source impedance of 2 (because port 1's 1 Ω is shared by two halves). Looking from port 2: $Z_{in}^e=Z^2/2$. Matched if $Z=\sqrt2$.
- *Odd mode* (ports 2 and 3 driven in anti-phase): the symmetry plane is a virtual ground; the λ/4 line shorted at the port-1 end looks open at port 2, so port 2 sees only $r/2$. Matched if $r/2=1$, i.e. $r=2$.
- Port 1 excitation is purely even (by symmetry); from it $S_{21}=S_{31}=-j/\sqrt2$, $S_{11}=0$.
- Isolation: a wave into port 2 decomposes as ½ even + ½ odd; both are perfectly absorbed/transmitted such that their contributions at port 3 cancel: $S_{23}=0$.
Check A: S at f₀ matches to $10^{-9}$ and $S^HS\neq I$ (the resistor absorbs odd-mode power).

**(c) Unequal Wilkinson.** With $P_3=K^2P_2$, the same even/odd reasoning with unequal arms gives $Z_{03}=Z_0\sqrt{(1+K^2)/K^3}$, $Z_{02}=K^2Z_{03}$, $R=Z_0(K+1/K)$; the outputs are naturally at impedances $Z_0K$ and $Z_0/K$ and need quarter-wave transformers back to $Z_0$ [1 §7.3]. Check B confirms the exact 2/3 : 1/3 split, match and isolation.

**(d) Lumped Wilkinson.** A λ/4 line of impedance $Z$ at $\omega_0$ has the same ABCD as a π-network of series $L=Z/\omega_0$ and shunt $C=1/(Z\omega_0)$ at each end (exactly, at $\omega_0$ only). Replacing both arms gives series 25.9 nH, 5.19 pF at each output, 2 × 5.19 pF at the input, 100 Ω — exact at 433.92 MHz, narrower band (17 % for 20 dB) than the distributed version (check C).

**(e) Branch-line hybrid.** Even/odd analysis about the horizontal symmetry plane reduces the four-port to two-ports made of a λ/4 series line of $Z_0/\sqrt2$ between open-stub (even) or short-stub (odd) λ/8 shunt lines of $Z_0$. Combining the even and odd transmission/reflection coefficients gives $S_{21}=-j/\sqrt2$, $S_{31}=-1/\sqrt2$, $S_{41}=0$, $S_{11}=0$ [1 §7.5]. Bandwidth is limited (≈ 10–20 % for 20 dB) because every arm is a quarter-wave; multi-section branch-lines widen it.

**(f) Rat-race.** Ports sit on a 1.5 λ ring of $\sqrt2Z_0$ at spacings λ/4, λ/4, λ/4, 3λ/4. From one port the paths to the two adjacent output ports differ by λ/2 in one case (anti-phase outputs) and by 0 in the other (in-phase outputs); the opposite port sees paths differing by λ/2 and cancels (isolation). Check E.

**(g) Coupled-line coupler.** A λ/4 section of symmetric coupled lines terminated in $Z_0=\sqrt{Z_{0e}Z_{0o}}$: even-mode and odd-mode waves see $Z_{0e}$ and $Z_{0o}$; the coupled (backward) port collects $(\Gamma_e-\Gamma_o)/2$, which at θ = 90° has magnitude $C=(Z_{0e}-Z_{0o})/(Z_{0e}+Z_{0o})$. The isolated port collects $(T_e-T_o)/2$, zero only if both modes have the **same electrical length** — true for TEM (stripline, coax) but not microstrip, where the even mode is slower. Inverting: $Z_{0e}=Z_0\sqrt{\frac{1+C}{1-C}}$, $Z_{0o}=Z_0\sqrt{\frac{1-C}{1+C}}$ [1 §7.6]. Tight coupling (3 dB) needs gaps too small for edge coupling → the **Lange coupler** interdigitates four or more fingers connected by bond wires to raise the odd-mode capacitance, giving 3 dB over an octave [1 §7.7][2].

**(h) Combining efficiency.** Feed two sources $a_2, a_3$ into the Wilkinson outputs: $b_1=-j(a_2+a_3)/\sqrt2$, so $\eta=|a_2+a_3|^2/(2(|a_2|^2+|a_3|^2))$. For equal amplitudes and phase difference Δφ, $\eta=\cos^2(\Delta\varphi/2)$; for amplitude ratio $r$ and equal phase, $\eta=(1+r)^2/(2(1+r^2))$. With N-way combining and one source dead, the output is $((N-1)/N)^2$ of the full power (check H). The "missing" power is dissipated in the isolation resistors — size them for the worst failure.

### Level 3 — generalisations and limits
- **Scattering-matrix view of hybrids**: an ideal 90° hybrid has $S=\frac{-1}{\sqrt2}\begin{bmatrix}0&j&1&0\\j&0&0&1\\1&0&0&j\\0&1&j&0\end{bmatrix}$; a 180° hybrid $\frac{-j}{\sqrt2}\begin{bmatrix}0&1&1&0\\1&0&0&-1\\1&0&0&1\\0&-1&1&0\end{bmatrix}$ [1]. Both are lossless, matched, reciprocal four-ports (allowed, unlike three-ports).
- **Balanced amplifiers** use two 90° hybrids: reflections from the two identical amplifiers arrive at the input port in anti-phase and cancel, going to the terminated port instead — good input match with noise-matched LNAs and +3 dB power ([LNA](lna-design.md#level-3--invariants-limits-and-alternative-topologies)).
- **Broadband dividers:** multi-section Wilkinsons (Cohn 1968) reach decade bandwidths; resistive and transformer (ferrite) splitters cover multiple octaves at lower frequencies ([baluns & transformers](baluns-and-rf-transformers.md)).
- **Directivity limits:** microstrip couplers' directivity is set by the mode-velocity mismatch and by connector/termination mismatch; any port mismatch $\Gamma$ creates an error signal of order $|\Gamma|$ at the coupled port, so a coupler with 20 dB directivity cannot measure return loss much better than ~20 dB (see [VNA fundamentals](../17-test-measurement/vna-fundamentals-calibration.md)). Compensation: lumped capacitors at the coupled-line ends, wiggly (sawtooth) edges, dielectric overlay, or stripline.
- **Phased-array feeds**: corporate Wilkinson trees give equal amplitude/phase; the isolation resistors absorb reflections from mismatched elements, improving scan behaviour ([beamforming architectures](../12-phased-arrays/beamforming-architectures.md)).

### Level 3 — the non-ideal Wilkinson and incoherent combining
**(a) Lossy arms: choosing R.** For a symmetric three-port viewed from ports 2 and 3, $S_{22}=(\Gamma_e+\Gamma_o)/2$ and $S_{23}=(\Gamma_e-\Gamma_o)/2$, where $\Gamma_e,\Gamma_o$ are the even- and odd-mode reflections. Isolation needs $\Gamma_e=\Gamma_o$; match needs $\Gamma_e=-\Gamma_o$. Ideal arms give both as zero.
- *Even mode with a lossy quarter-wave arm* ($\tanh(\alpha l+j\pi/2)=\coth\alpha l\approx1/\alpha l$) terminated in $2Z_0$: $Z_e\approx Z_0[1+\alpha l(2Z_0/Z-Z/2Z_0)]=Z_0(1+0.707\alpha l)$ for $Z=\sqrt2Z_0$.
- *Odd mode:* the shorted lossy arm looks like $Z/\alpha l$ in parallel with $R/2$.
- Equating $\Gamma_o$ to $\Gamma_e$ gives
$$R_{opt}\approx2Z_0\,(1+\sqrt2\,\alpha l).$$
Script: arm loss 0.125 / 0.25 / 0.5 dB gives $R_{opt}$ = 102.1 / 104.2 / 108.5 Ω (formula 102.0 / 104.1 / 108.1). With the standard 100 Ω the isolation is only 46 / 40 / 34 dB, and the optimum restores it to > 160 dB. The price is that the output match stays at −46 / −40 / −34 dB, since $\Gamma_e$ is no longer zero. Real isolation is usually limited first by resistor and pad parasitics: 0.3 / 0.6 / 1.0 nH in series with the 100 Ω gives 38.8 / 32.7 / 28.3 dB at 2.45 GHz. Mount the resistor across the closest-spaced ends of the arms, or use a thin-film chip with a small footprint.

**(b) Unbalanced or mismatched loads.** Because $S_{22}=S_{33}=S_{23}=0$, there is no multiple-reflection path between the outputs. With loads $\Gamma_2,\Gamma_3$:
$$\Gamma_{in}=S_{12}^2\Gamma_2+S_{13}^2\Gamma_3=-\frac{\Gamma_2+\Gamma_3}{2}\quad(\text{exact; checked on 50 random load pairs}).$$
A wave reflected from one output splits **50 % back to the input, 50 % into the resistor, 0 % to the other output**. That is the isolation property, and the resistor rating must cover it. One mismatched antenna in a Wilkinson-fed array therefore disturbs neither its neighbour nor, by more than half its reflection, the source.

**(c) Outputs tied together.** Short ports 2 and 3 together. The resistor then carries no current, so only the even mode exists, and each arm sees twice the common load. Into 25 Ω each arm sees 50 Ω, transforms it to 100 Ω, and the two in parallel give 50 Ω: **$S_{11}=0$**. Into 50 Ω each arm transforms 100 Ω to 50 Ω, and the parallel pair gives 25 Ω: **$S_{11}=(25-50)/75=-1/3$** (both checked).

**(d) Correlated vs uncorrelated inputs.** Feed waves $a_2,a_3$ into the outputs. The input-port wave is $b_1=-j(a_2+a_3)/\sqrt2$:
- *Coherent, equal, in phase:* $|b_1|^2=2P$, with nothing in the resistor (the even mode only).
- *Uncorrelated* (different frequencies, independent noise, two unsynchronised transmitters): the cross term averages to zero, so $\overline{|b_1|^2}=\tfrac12(P_2+P_3)$. Two equal uncorrelated inputs give **P at the output and P in the resistor**. This is not a defect: a matched, lossless-to-the-input combiner *cannot* add incoherent powers. Each input's odd-mode half is absorbed.
- *Noise of the combiner itself:* for a passive network at temperature T, the internal noise waves have correlation matrix $C=kT(I-SS^H)$ (Bosma's theorem). For the ideal Wilkinson, $C_{11}=0$: **the resistor's noise does not reach the input/sum port**. At ports 2 and 3 it contributes kT/2 each, perfectly anti-correlated (odd mode).
- *Array consequence:* after per-element LNAs the signals add coherently and the LNA noises incoherently. Two elements combined in a Wilkinson give +3.01 dB SNR over one (verified), and N elements give 10 log N, with the resistors absorbing the incoherent remainder ([beamforming architectures](../12-phased-arrays/beamforming-architectures.md)). The combiner's ohmic loss (not the resistor) adds noise in the usual way.

**(e) As a PA combiner into a bad antenna.** A wave reflected by the antenna enters port 1 and splits, in even mode, **50 % to each PA** and 0 % to the resistor. The combiner protects each PA from the *other* PA's failure (odd mode), not from the antenna. Use an isolator or foldback for that ([PA control](pa-control-protection-and-sequencing.md)).

### Level 3 — broadband transformer hybrids (0°/180°), multi-octave splitters and receiver multicouplers
All numbers here come from `tools/verify/s15_tlt_splitter.py` (ngspice). The script models the hybrid winding as a **discretised bifilar pair on ferrite**: self-inductance L per conductor, mutual kL, and inter-conductor capacitance C in 24 sections. With k → 1 and C = 0 this is a flux-coupled transformer. With finite k and C, the even-split path becomes a transmission line of $Z_{dm}=\sqrt{2L(1-k)/C}$, which is a transmission-line transformer (TLT).

**(a) The 0° "Mini-Circuits" splitter is a lumped Wilkinson.** A centre-tapped hybrid transformer T2 has its winding ends at the two outputs, the common port at the centre tap, and a 2Z₀ = 100 Ω resistor across the outputs. The two outputs in parallel present 25 Ω at the centre tap, so a matching transformer T1 (50 → 25 Ω, turns ratio √2 in the ideal case) brings the input back to 50 Ω [9], [10].
- *Even mode* (equal outputs): the currents from the centre tap flow out through the two half-windings in opposite senses, so the core flux cancels. No current flows in the resistor and there is no loss. In TLT language this is the line (differential) mode.
- *Odd mode* (imbalance or reflections): the half-windings aid, so the core presents its full magnetising/common-mode reactance and each output sees R/2 = 50 Ω. The resistor absorbs the power and the outputs are isolated.
- This is the same even/odd argument as for the Wilkinson ((b) above), with the λ/4 arms replaced by a transformer. Near-ideal parts (k = 0.99995) give S21 = S31 = −3.011 dB, 0.00° between outputs, RL ≈ 38 dB and 69 dB isolation at 100 MHz (check A1). Mini-Circuits builds these as two ferrite TLTs, one dividing and one matching [11].

**(b) Low-frequency edge.** Isolation fails first: the odd mode sees the full winding, $4L_{half}$ when k ≈ 1, in parallel with the 100 Ω resistor. With limits of IL within 0.5 dB of 3.01, RL > 15 dB and isolation > 20 dB, the lower edge sits where $2\pi f_L\cdot4L_{half}\approx$ 2.0–2.4 × 100 Ω: 24.2/5.41/1.26 MHz for $L_{half}$ = 0.4/1.6/6.4 µH (check A2). So **L sets f_L**: four times the inductance gives a quarter of the frequency, which means 2× the turns, or a higher-µ ferrite at the cost of more core loss.

**(c) High-frequency edge: leakage vs line.**
- *Flux-coupled winding.* In the even mode the leakage $2(1-k)L$ appears as a series inductance. With $L_{half}$ = 1.6 µH it is 32 nH at k = 0.99 (upper edge 168 MHz) and 3.2 nH at k = 0.999 (1.5 GHz). Real windings add uncontrolled inter-winding capacitance on top, which resonates with the leakage.
- *TLT (bifilar or twisted-pair) winding.* The leakage and the capacitance form a deliberate line of impedance $Z_{dm}$ and delay $t_d$. For a fixed line length the best impedance is **Z_dm ≈ 50 Ω**: 910 MHz at 64 ps and 298 MHz at 200 ps, against ≈ 20 % lower with 25 or 100 Ω. The top edge comes where the line is **≈ 21° long** ($f_{hi}\approx0.06/t_d$) (check A3). Design rule: wind the hybrid as a 50 Ω pair, keep it as short as the low-edge inductance allows, and use the highest-µ core that is still low-loss at f_hi.
- *Why commercial splitters reach a decade or more.* Low edge from turns × µ, top edge from line length: e.g. 5–500 MHz from a few bifilar turns on a small ferrite bead or binocular core, where every millimetre of wire counts.

**(d) 180° hybrid transformer.** Add a third winding (the Δ port) coupled to the whole centre-tapped winding, with $L_\Delta=2L_{half}$ (turns $\sqrt2\,n$). This transforms 50 Ω on Δ to 100 Ω across the outputs. The centre tap (Σ) keeps its 50 → 25 Ω transformer. Driving Σ gives in-phase outputs (−3.01 dB each); driving Δ gives outputs exactly 180.00° apart. Σ and Δ are mutually isolated (to numerical precision) and the outputs are isolated by 68 dB at 100 MHz (check B1). **The 0° splitter's 100 Ω resistor *is* the terminated Δ port**: bring that port out and you have a four-port 0°/180° hybrid (sum/difference networks, balanced mixers and push-pull combiners). Ferrite 180° hybrids are limited to roughly the low-GHz range (≈ 3 GHz, per a patent's background statement [12]); above that use rat-race, Marchand or coupled-line hybrids ((f) above; [baluns](baluns-and-rf-transformers.md)).

**(e) Multi-octave splitters, compared.**

| Type | Bandwidth | Loss / isolation | Use |
|---|---|---|---|
| Transformer/TLT hybrid (this section) | decade+, kHz to low GHz | ≈ 3.3–3.8 dB per 2-way, 20–35 dB isolation (typical catalogue values, not verified here) | HF–UHF splitting, receiver multicouplers |
| Multi-section Wilkinson (Cohn [4]) | octave to decade at microwave | ≈ 0.5–1 dB excess, ≥ 20 dB (typical, not verified here) | microwave arrays, test |
| Resistive star | DC to many GHz | 6 dB, 6 dB isolation | test, levelling |
| Single λ/4 Wilkinson | ≈ 36 % (20 dB) | low | narrowband |

**(f) Receiver multicouplers: amplify, then split.** Splitting one antenna passively to N receivers adds 10 log N + excess loss directly to every receiver's noise figure. Put a low-noise, high-IP3 amplifier first. Example: a 433 MHz ground station feeding 4 receivers (NF 6 dB, IIP3 −10 dBm) through a 4-way splitter with 6.5 dB total loss (check C):

| Front end | System NF | System IIP3 |
|---|---|---|
| passive split | **12.5 dB** | −3.5 dBm |
| LNA: G 20 dB, NF 1 dB, OIP3 +15 dBm, then split | **1.54 dB** | −23.6 dBm |
| LNA: G 12 dB, NF 1 dB, OIP3 +22 dBm, then split | **3.65 dB** | −15.5 dBm |

Choose multicoupler gain only a little above the split loss plus what the receivers' NF needs, because every extra dB of gain comes straight off the IIP3. Use an isolating splitter, not a resistive star: a receiver that leaks −50 dBm of LO out of its antenna port reaches its neighbours at −75 dBm through 25 dB isolation, but at −56 dBm through a resistive star. Notch or filter any co-sited transmitter ahead of the amplifier ([co-site](co-site-interference-and-transmitter-intermod.md), [receiver architectures](receiver-architectures.md)).

## Design equations & rules of thumb

| Component | Design equations | Notes |
|---|---|---|
| Wilkinson (equal) | arms λ/4 of $\sqrt2Z_0$; $R=2Z_0$ | 70.7 Ω, 100 Ω; ≈ 36 % BW (20 dB) |
| Wilkinson (unequal, $P_3/P_2=K^2$) | $Z_{03}=Z_0\sqrt{(1+K^2)/K^3}$, $Z_{02}=K^2Z_{03}$, $R=Z_0(K+1/K)$ | outputs $Z_0K$, $Z_0/K$ → transform |
| Lumped λ/4 | $L=Z/\omega_0$, $C=1/(Z\omega_0)$ each end | narrower band |
| Branch-line | series arms $Z_0/\sqrt2$, shunt arms $Z_0$ | 35.4 / 50 Ω |
| Rat-race | ring $\sqrt2Z_0$, circumference 1.5 λ | 70.7 Ω |
| Coupled-line | $Z_{0e,o}=Z_0\sqrt{(1\pm C)/(1\mp C)}$ | λ/4 long; C as voltage ratio |
| Short weak coupler | $C\approx k\sin\theta$, rises 6 dB/octave | power sampling |
| Directivity | $D=C_{3}/C_{4}$ (dB difference) | microstrip ~10 dB, stripline 25–40 dB |
| Resistive star | 3 × $Z_0/3$ | −6 dB each, 6 dB isolation |
| Combining | $\eta=\cos^2(\Delta\varphi/2)$; dead PA: $((N-1)/N)^2$ | |
| Transformer 0° splitter | centre-tapped hybrid + $2Z_0$ + $Z_0\to Z_0/2$ transformer | lumped Wilkinson; decade+ |
| Hybrid low edge | $2\pi f_L\cdot4L_{half}\approx2\cdot2Z_0$ | 1.6 µH half-winding → 5.4 MHz |
| TLT hybrid top edge | $Z_{dm}\approx Z_0$; $f_{hi}\approx0.06/t_d$ | line ≈ 21° long at f_hi |
| 180° transformer hybrid | Δ winding $L_\Delta=2L_{half}$ | Δ termination = the 0° splitter's resistor |
| Multicoupler | Friis: LNA NF + (split loss × Rx F − 1)/G | gain costs IIP3 dB-for-dB |

## Worked examples

### Example 1 — 2.45 GHz microstrip Wilkinson on 0.8 mm FR-4
$\sqrt2\cdot50=70.7\ \Omega$ → W = 0.81 mm (εeff 3.17), λ/4 = 17.2 mm at 2.45 GHz; R = 100 Ω 0402 thin-film between the outputs, placed so both leads are as short as possible (its parasitic inductance and the gap between the arms limit isolation above a few GHz). Ideal response: 20 dB RL/isolation over 2.01–2.89 GHz (script A). Curve the arms into a circle or meander to keep the resistor ends close. For phased-array or MIMO splitting, a tree of these gives 2ⁿ outputs; each level adds ≈ 0.2–0.4 dB loss on FR-4.

### Example 2 — 433.92 MHz lumped Wilkinson (e.g. to combine two antennas or split to two receivers)
L = 25.9 nH (use 27 nH or 24 + 1.8 nH wire-wound), C = 5.19 pF at each output (5.1 pF C0G), 10.4 pF at the input (10 pF), R = 100 Ω. Exact at f₀; 20 dB match/isolation 394–466 MHz (script C). Finite inductor Q (≈ 40) adds ≈ 0.1–0.2 dB loss; the 100 Ω can be an 0402 thick-film — at 433 MHz its parasitics are negligible.

### Example 3 — quadrature hybrid feeding a dual-fed RHCP GNSS patch
A square patch fed at two orthogonal edges with equal amplitude and 90° phase radiates circular polarisation (see [patch antennas](../08-antennas/patch-antennas.md)). A branch-line at 1575.42 MHz: 35.4 Ω series arms, 50 Ω shunt arms, isolated port terminated in 50 Ω. Over 1559–1610 MHz (Beidou B1/GPS/Galileo E1/GLONASS G1): amplitude imbalance ≤ 0.03 dB, phase 90.00–90.01°, RL and isolation ≥ 27.6 dB (script D) — the hybrid contributes < 0.03 dB of axial-ratio degradation; the antenna's own element imbalance will dominate. Bonus: reflections from the patch go to the hybrid's terminated port, so the LNA sees a good match even if the patch is detuned.

### Example 4 — forward/reflected power sampling for a 433 MHz 2 W PA
A λ/4 coupled-line coupler at 433 MHz is ≈ 90 mm long on FR-4 — too big. Options:
- **Short weak coupled section**: e.g. a 10°-long pair with $Z_{0e}/Z_{0o}$ = 52/48 Ω couples −43.2 dB at 434 MHz (script I), rising 6 dB/octave (−37.3 dB at 868 MHz). At +33 dBm this delivers ≈ −10 dBm to a detector — ideal for a log detector (see [detectors](detectors-and-power-meters.md)). Directivity will be poor in microstrip, so reflected-power readings are only indicative.
- **Transformer (ferrite) directional coupler** or a commercial SMT coupler for accurate VSWR protection.

### Example 5 — combining two 1 W PAs
Two SKY66122-class FEMs combined in a Wilkinson: with 30° phase mismatch, 93 % of the power reaches the output (−0.3 dB); the other 7 % (≈ 140 mW at 2 W total) heats the 100 Ω resistor — use a ≥ 0.25 W part, or ≥ 1 W to survive one PA failing: the output then drops to 25 % of the combined 2 W (0.5 W, i.e. half of the surviving PA's 1 W) and the other 0.5 W goes into the resistor — assuming the dead PA's port still looks like 50 Ω; if it reflects, the power sloshes back and the surviving PA sees a mismatch.

### Example 6 — 10 dB and 20 dB microstrip couplers (why directivity is poor)
0.8 mm FR-4, 2.45 GHz: 10 dB coupler $Z_{0e}/Z_{0o}$ = 69.4/36.0 Ω → W = 1.30 mm, S = 0.13 mm (εeff even/odd 3.57/2.80): coupling 10.07 dB, **directivity 11.3 dB**; 20 dB coupler 55.3/45.2 Ω → W = 1.51, S = 1.16 mm: coupling 20.0 dB, **directivity 5.9 dB** (script F). Ideal TEM (stripline) versions have infinite directivity. The 0.13 mm gap is near the limit of standard PCB processes.

### Example 7 — Combining two receivers' antennas vs combining two radios
- **Two 433 MHz antennas into one receiver** (pattern diversity on a rocket): the signals are coherent, but their phases differ with attitude. When they arrive in anti-phase the sum port gets nothing, and the energy goes into the resistor, as a deep pattern null. The noise from the two antennas is uncorrelated and is halved, so the SNR follows $\cos^2(\Delta\varphi/2)$ × 2. Expect nulls as the rocket rolls; a switch-and-pick (selection) diversity scheme avoids them.
- **Two transmitters on different channels into one antenna through a Wilkinson:** each loses 3 dB into the resistor, because the signals are uncorrelated. Each transmitter also sees the other only through the isolation (≈ 20–30 dB in practice), so transmitter IMD still occurs ([co-site](co-site-interference-and-transmitter-intermod.md)). For different *bands* use a diplexer, which loses only about 0.2 dB ([diplexers](duplexers-diplexers-and-crystal-filters.md)).

### Example 8 — A 433 MHz ground-station multicoupler for four receivers
Antenna → 433 MHz SAW or helical band-pass (to stop out-of-band blockers) → LNA (NF 1 dB, 12–20 dB gain, OIP3 ≥ +20 dBm) → a 4-way transformer or Wilkinson splitter (two levels of 2-way; ≈ 6.5 dB) → SDR, LoRa receiver, spectrum analyser and spare (terminate unused ports in 50 Ω, or the isolation of the other ports suffers).
- System NF falls from 12.5 dB (passive) to 1.5–3.7 dB, depending on LNA gain (check C).
- The LNA's OIP3 then sets the strong-signal limit: with a 20 dB LNA the system IIP3 is −24 dBm, so a nearby +30 dBm transmitter would need ≥ 50 dB of filtering before the LNA.
- Because the SDR's LO leakage reaches the other receivers only through the splitter isolation, an isolating splitter beats a resistive one by ≈ 20 dB here.

## Practical notes
- **Resistors:** thin-film 0402/0603 for Wilkinsons above ~2 GHz; check the power rating for combiners (failure case).
- **Symmetry:** amplitude/phase balance depends on physical symmetry — keep both arms identical, including vias and bends; for phased arrays, match the whole tree.
- **Termination quality:** a hybrid's isolation is only as good as the load on its fourth port; use a 50 Ω resistor with a short ground via, not a long trace.
- **Commercial parts:** SMT 90° hybrids (e.g. TTM/Anaren Xinger), Mini-Circuits splitters and couplers (LTCC and transformer types) — usually smaller and better characterised than printed ones below ~2 GHz; see [components](../18-components-parts/rf-switches-attenuator-parts.md).
- **Measuring directivity:** terminate the through port with a very good load, measure coupled and isolated responses with a VNA; any connector mismatch sets a floor.
- **Splitting for test:** a resistive 6 dB splitter is the right tool for making a VNA ratio measurement or feeding two instruments; a Wilkinson is narrowband.

## Common mistakes & misconceptions
- *"A Wilkinson's resistor wastes half the power."* In even-mode (normal) division it carries no current; it only absorbs odd-mode power (imbalance, mismatch).
- *"Any T-junction with λ/4 transformers is a Wilkinson."* Without the resistor there is no output isolation and outputs interact.
- *"Splitting to N outputs loses 10 log N dB."* That is the intended division, not loss; the *excess* loss (line/resistor losses) is what matters.
- *"My coupler has 20 dB coupling, so it has 20 dB directivity."* Unrelated quantities; microstrip directivity is often only 5–15 dB.
- *"Combining two PAs always gives +3 dB."* Only with matched amplitude and phase; 90° error loses half.
- *"A resistive splitter isolates the outputs."* Only by 6 dB.
- *"A transformer splitter is just a T with a transformer."* The centre-tapped hybrid and its resistor provide the isolation (odd mode). Without them the outputs interact exactly as in a bare T.
- *"More turns always extend the bandwidth."* More turns lower f_L but lengthen the line, so f_hi falls (≈ 0.06/t_d). Use a higher-µ core to get L with fewer turns.
- *"Wind the TLT hybrid as a 100 Ω pair because the resistor is 100 Ω."* The even (line) mode wants ≈ 50 Ω; 25 or 100 Ω pairs lose ≈ 20 % of the top edge.
- *"Splitting an antenna to several receivers only costs 3 dB per split."* It adds that loss straight to each receiver's NF; put an LNA first (multicoupler).
- *"A branch-line hybrid is broadband."* Every arm is λ/4 → ≈ 10–20 % bandwidth; use multi-section or coupled-line (Lange) hybrids for more.

- *"A Wilkinson combines any two signals with 3 dB gain."* Only coherent, in-phase ones. Uncorrelated signals lose half their power in the resistor.
- *"The isolation resistor protects the PAs from antenna reflections."* Antenna reflections return to the PAs in even mode; the resistor only absorbs odd-mode (imbalance) power.
- *"Use exactly 2 Z₀ for the resistor."* With lossy arms the isolation optimum is slightly higher ($2Z_0(1+\sqrt2\alpha l)$), and parasitics often matter more.

## How to simulate / verify
- `tools/verify/rfckt_couplers.py`: equal/unequal/lumped Wilkinson, branch-line with axial-ratio estimate, rat-race, coupled-line couplers (TEM vs microstrip modal velocities via Garg–Bahl), resistive splitter, combining efficiency, short weak coupler. Uses `tools/verify/rfckt_netsolve.py` — a small nodal solver (terminated-nodal-matrix method, self-tested; note that naive Kron reduction to port Y-parameters fails exactly at f₀ for cascaded quarter-wave lines, whose Y-matrix does not exist).
- `tools/verify/s15_tlt_splitter.py` (W5-S15, ngspice): transformer 0° splitter with a discretised bifilar hybrid (flux-coupled vs TLT), low/high band edges, best line impedance, 180° hybrid with Δ winding, multicoupler cascade (also the feedback/push-pull PA checks for [power amplifiers](power-amplifiers.md)). ALL PASS, ≈ 3 s.
- `tools/verify/rf2_wilkinson_nonideal.py` (W5-E7): lossy-arm optimum R, unbalanced loads, tied outputs, coherent/incoherent combining and noise correlation $C=kT(I-SS^H)$, combiner into a mismatch, resistor inductance. ALL PASS.
- scikit-rf `media.DefinedGammaZ0` / `MLine` and `Circuit` can build the same networks; openEMS for layout (junction and bend effects, resistor pads).
- Bench: VNA with the unused ports terminated (a 2-port VNA measures a 3/4-port device one pair at a time).

## Open questions / gaps
- Lange coupler design equations (Ou 1975; Presser 1978) are only described, not implemented.
- The bifilar-winding model couples only conductors within each section (neglecting inter-section mutual inductance and ferrite loss/µ dispersion), so its band edges are idealised. No commercial splitter was measured, and the catalogue loss/isolation figures in the multi-octave table are typical values.
- No Cohn multi-section Wilkinson was synthesised or simulated here.
- The microstrip coupler results use static Garg–Bahl modal parameters (checked against an FD solver in `rfckt_filters.py` within ≈ 4 %), without dispersion or discontinuities; an EM check would refine directivity numbers.
- No measured data for commercial SMT hybrids/couplers gathered here (belongs in domain 18).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — §7.1 (three-port properties), §7.3 (Wilkinson, even/odd analysis, unequal split), §7.5 (quadrature hybrid), §7.6 (coupled-line couplers), §7.7 (Lange), §7.8 (180° hybrid). (textbook)
2. J. Lange, "Interdigitated stripline quadrature hybrid," *IEEE Trans. MTT*, 17(12), pp. 1150–1151, Dec. 1969. (peer-reviewed)
3. E. J. Wilkinson, "An N-way hybrid power divider," *IRE Trans. MTT*, 8(1), pp. 116–118, Jan. 1960. (peer-reviewed; original divider)
4. S. B. Cohn, "A class of broadband three-port TEM-mode hybrids," *IEEE Trans. MTT*, 16(2), pp. 110–116, Feb. 1968 (multi-section Wilkinson). (peer-reviewed)
5. R. Garg, I. J. Bahl, "Characteristics of coupled microstriplines," *IEEE Trans. MTT*, 27(7), pp. 700–705, 1979 (modal parameters used for the microstrip coupler). (peer-reviewed)
6. R. K. Mongia, I. J. Bahl, P. Bhartia, J. Hong, *RF and Microwave Coupled-Line Circuits*, 2nd ed., Artech House, 2007 (coupler directivity compensation). (textbook; background)
7. H. Bosma, "On the theory of linear noisy systems," *Philips Research Reports Supplements*, no. 10, 1967 (noise-wave correlation $C=kT(I-SS^H)$ of passive networks). (peer-reviewed/report; cited)
8. `tools/verify/rf2_wilkinson_nonideal.py` (this KB; W5-E7 non-ideal Wilkinson section).
9. Mini-Circuits, AN-10-006 *Understanding power splitters* — T-junction isolation, centre-tapped transformer hybrid with internal resistor, 25 Ω input impedance needing a matching transformer. https://www.minicircuits.com/app/AN10-006.pdf (app note; via search excerpts)
10. J. Sevick, *Transmission Line Transformers*, 4th ed., Noble/SciTech, 2001 — TLT hybrids and combiners, line impedance and length limits. (textbook; cited)
11. Mini-Circuits, AN-10-001 (TCP-series splitters: one ferrite TLT for division plus one for matching; ferrite splitters below 1 GHz with multi-decade bandwidth). https://www.minicircuits.com/app/AN10-001.pdf (app note; via search excerpts)
12. US 7 746 193, "Miniature 180 degree hybrid coupler" — background notes ferrite 180° hybrids are limited to ≈ 3 GHz. (patent; background statement only)
13. `tools/verify/s15_tlt_splitter.py` (this KB; W5-S15).
