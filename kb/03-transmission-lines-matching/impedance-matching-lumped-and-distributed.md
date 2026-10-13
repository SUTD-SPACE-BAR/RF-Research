---
title: Impedance matching — lumped and distributed
domain: 03-transmission-lines-matching
slug: impedance-matching-lumped-and-distributed
tags: [impedance-matching, l-network, pi-network, t-network, loaded-q, bandwidth, stub-tuning, double-stub, forbidden-region, quarter-wave, binomial-transformer, chebyshev-transformer, klopfenstein-taper, component-q, chip-antenna, pi-pad, vna, differential-matching, half-circuit, detector-matching, interstage-matching, de-embedding]
prerequisites:
  - reflections-vswr-return-loss-mismatch.md
  - input-impedance-stubs-quarter-wave.md
  - smith-chart.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../01-circuit-theory/network-theorems-max-power-transfer.md
related:
  - broadband-matching-bode-fano.md
  - planar-lines-microstrip-stripline-cpwg.md
  - s-parameters.md
  - ../04-real-components-hf/inductors-at-rf.md
  - ../04-real-components-hf/capacitors-at-rf-mlcc.md
  - ../04-real-components-hf/component-models-s2p-spice.md
  - ../08-antennas/antenna-matching-and-baluns.md
  - ../08-antennas/pcb-and-chip-antennas.md
  - ../06-rf-circuits/power-amplifiers.md
  - ../06-rf-circuits/lna-design.md
  - ../17-test-measurement/nanovna-librevna-practical.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Impedance matching — lumped and distributed

## Questions this page answers
- How do I design an L-network, and where does $Q=\sqrt{R_h/R_l-1}$ come from?
- How do I match a complex load such as a chip antenna measured as 18 − j35 Ω?
- When should I use a Pi or T network instead of an L, and how do I pick Q?
- How much bandwidth do I get, and how much loss do real 0402 inductors add?
- How do single-stub, quarter-wave, binomial, Chebyshev and Klopfenstein matching work, and when do they beat lumped parts?
- What is the practical procedure for tuning a pi pad on my PCB with a NanoVNA?
- Is the best match always the conjugate match? (Not for PAs and LNAs.)
- Why did my perfect simulated match fail on the real board?
- If a matching network "just moves the reflection", where does the reflected power go?
- Why does my extracted component model contain a negative inductance?
- How do I use the S11 or impedance table in an RF IC's datasheet — do I conjugate it or not?
- How do I match a differential (balanced) IC input?
- How do I match a diode detector whose impedance is several kilohms?
- How do I match one transistor stage to the next without going through 50 Ω?
- Why can't a double-stub tuner match every load?

## TL;DR
- **L-network** between resistances $R_h>R_l$: $Q=\sqrt{R_h/R_l-1}$, series reactance $|X_s|=QR_l$ on the low-R side, shunt reactance $|X_p|=R_h/Q$ on the high-R side. Two solutions (low-pass or high-pass). 12.5 → 50 Ω at 433 MHz: 7.96 nH series, 12.73 pF shunt.
- **Complex loads**: two closed-form solutions each (Pozar §5.1); choose the one with realistic component values, lower Q and (for transmitters) low-pass shape for harmonic rejection.
- **Pi / T networks** add a third element so you can *choose* Q (≥ the L-network's). Bandwidth (RL > 10 dB) for 10 → 50 Ω at 915 MHz: L (Q = 2) 38 %, Pi Q = 3: 21 %, Q = 5: 10 %, Q = 8: 6 %, Q = 12: 3.9 % — roughly **BW ≈ 0.5/Q** for Q ≥ 5.
- **Loss with real components**: $IL\approx10\log_{10}(1+Q_n/Q_L+Q_n/Q_C)$ dB (checked to within 5 %). A 5 → 50 Ω L-match with $Q_L=20$ inductors costs 0.67 dB; with $Q_L=40$, 0.36 dB. Low-R transformations are expensive.
- **Distributed**: single shunt stub (two solutions per load), λ/4 transformer (after rotating a complex load to the real axis), multi-section **binomial** (maximally flat) and **Chebyshev** (equiripple, wider), continuous **Klopfenstein** taper (shortest for given ripple; passband starts at $\beta L=A=\cosh^{-1}(\Gamma_0/\Gamma_m)$, ≈0.7 λ for 5:1 at Γm = 0.02).
- Small-reflection-theory designs (binomial BW formula, Chebyshev synthesis, Klopfenstein) are accurate for 2:1 ratios but **overshoot the ripple by 20–35 % at 5:1** — verify with an exact cascade (our script) and refine.
- **Special cases** (§ [Special topics](#special-topics)): a lossless match makes the internal bounces cancel at the input — the load's forward power rises to $P/(1-|\Gamma_L|^2)$ (1.56 W per watt for 12.5 Ω) and the stored energy equals $Q_n$ per radian; **negative L or C** in an extracted model means a reference plane is too far in; datasheet **$Z_\text{opt}$ is presented as is** (conjugating it by mistake is a |Γ| 0.6 error), input S11 is conjugate-matched; **differential** loads are matched on the half circuit (series elements per leg, shunt elements become one across-pair element with **2× the impedance**); a **kΩ detector** gains ≈ 20 dB of sensitivity from a reactive match; **interstage** matches go device-to-device directly (−0.39 dB vs −0.65 dB via 50 Ω in the example).
- **Double stub**: with spacing d, a load whose normalised conductance at the first stub exceeds $1/\sin^2\beta d$ (2 for λ/8 or 3λ/8 spacing) cannot be matched — move the stubs or add line.
- **Practical rule**: at 433/915 MHz on a flight computer use lumped L/Pi networks in a 3-pad "pi" footprint; at 2.4 GHz and above distributed elements become compact; always tune on the *assembled* board with a calibrated VNA, including parasitics and the enclosure/airframe.

## Intuition (no math)
A matching network is a *lossless impedance transformer*. The trick is resonance: a series reactance with a small resistance behaves, at one frequency, like a much larger resistance in parallel with a reactance (and vice versa). Put a series inductor in front of a 12.5 Ω load and the combination "looks like" a big resistor in parallel with an inductor; add a shunt capacitor that resonates that inductor away and you are left with just the big resistor — choose values so it is 50 Ω. The price of a large step-up is a large circulating reactive energy relative to the power delivered, which is exactly what **Q** measures. High Q means narrow bandwidth and, because real inductors and capacitors have loss, more of your power turned into heat.

Distributed matching does the same thing with pieces of line: a line rotates the load around the Smith chart until its conductance (or resistance) is right, and a stub adds the reactance that cancels what is left. Multi-section transformers and tapers spread one big mismatch into many small ones, arranged so that their reflections cancel over a band.

Conjugate matching ($Z_S=Z_L^*$) delivers the maximum power from a *given* source. A reflectionless match ($Z_L=Z_0$) is what cables and filters want. For a power amplifier or an LNA neither is automatically right: the PA wants the load that lets its transistor swing full voltage and current (the load line), and the LNA wants the source impedance that minimises noise — these are design choices, not "maximum power transfer".

## The math

### Level 1 — the L-network in four lines
For resistive terminations $R_h>R_l$:
$$Q_n=\sqrt{\frac{R_h}{R_l}-1},\qquad |X_s|=Q_nR_l\;(\text{series, on the }R_l\text{ side}),\qquad |X_p|=\frac{R_h}{Q_n}\;(\text{shunt, on the }R_h\text{ side}).$$
Opposite signs: series L with shunt C (**low-pass**, attenuates harmonics) or series C with shunt L (**high-pass**, passes DC blocking… and harmonics). Component values: $L=X/\omega$, $C=1/(\omega X)$.

### Level 2 — derivations

**Series ↔ parallel conversion.** A series pair $R_s+jX_s$ equals, at one frequency, a parallel pair $R_p\parallel jX_p$ with
$$R_p=R_s(1+Q^2),\quad X_p=X_s\frac{1+Q^2}{Q^2},\quad Q=\frac{|X_s|}{R_s}=\frac{R_p}{|X_p|}.$$
(Invert $Z=R_s+jX_s$ into $Y=G+jB$.) So adding series reactance to $R_l$ makes it look like $R_l(1+Q^2)$ in parallel with a reactance. Set $R_l(1+Q^2)=R_h$ → $Q_n=\sqrt{R_h/R_l-1}$, and cancel the parallel reactance with an opposite shunt element of value $X_p$ → $|X_p|=R_h/Q_n$. The network then presents $R_h$ at the shunt side. Verified: 12.5 → 50 Ω gives exactly 50 Ω (`tools/verify/tline_matching.py`, also via a scikit-rf cascade).

**Complex loads (Pozar §5.1).** With $Z_L=R_L+jX_L$ and target $Z_0$:
- $R_L>Z_0$ (shunt element across the load, series element toward the source):
$$B=\frac{X_L\pm\sqrt{R_L/Z_0}\sqrt{R_L^2+X_L^2-Z_0R_L}}{R_L^2+X_L^2},\qquad X=\frac1B+\frac{X_LZ_0}{R_L}-\frac{Z_0}{BR_L}.$$
- $R_L<Z_0$ (series element at the load, shunt toward the source):
$$X=\pm\sqrt{R_L(Z_0-R_L)}-X_L,\qquad B=\pm\frac{1}{Z_0}\sqrt{\frac{Z_0-R_L}{R_L}}.$$
Positive $X$ = inductor, negative = capacitor; positive $B$ = capacitor, negative = inductor. (If $R_L>Z_0$ but the admittance lies inside the $g=1$ circle the other topology may also work; the Smith chart shows which.) Ten load/solution cases verified to 10⁻⁹ Ω.

**Pi and T networks.** A Pi (shunt–series–shunt) is two L-networks back to back through an imaginary *virtual resistance* $R_v$ smaller than both terminations; a T (series–shunt–series) uses $R_v$ larger than both. Choose the loaded Q, set $R_v=R_h/(Q^2+1)$ (Pi) or $R_v=R_l(Q^2+1)$ (T), then design each half as an L-network ($Q_1=\sqrt{R_s/R_v-1}$, $Q_2=\sqrt{R_L/R_v-1}$) and merge the two middle series (Pi) or shunt (T) reactances. The minimum achievable Q is the L-network's $Q_n$; any higher Q is available. Why choose higher Q? Harmonic suppression (a PA's Pi filter), component values that exist (e.g. avoiding 0.3 pF), or fitting a fixed footprint.

**Bandwidth vs Q.** For a single resonant transformation the loaded Q sets the fractional bandwidth; for the example 10 → 50 Ω at 915 MHz, sweeping ideal components (script):

| Network | Q | C1 | L | C2 | BW for RL > 10 dB |
|---|---|---|---|---|---|
| L (low-pass) | 2.0 | 6.96 pF shunt | 3.48 nH | — | 38.0 % |
| Pi | 3 | 10.44 pF | 3.48 nH | 17.39 pF | 21.2 % |
| Pi | 5 | 17.39 pF | 2.36 nH | 35.65 pF | 10.4 % |
| Pi | 8 | 27.83 pF | 1.53 nH | 60.25 pF | 6.0 % |
| Pi | 12 | 41.75 pF | 1.04 nH | 92.04 pF | 3.9 % |

(L-network values: series $X_s=Q_nR_l=20$ Ω → 3.48 nH, shunt $X_p=50/2=25$ Ω → 6.96 pF.) Rule of thumb from these numbers: $BW_{RL>10\,\text{dB}}\approx0.5/Q$ for $Q\gtrsim5$. For broadband needs, *cascade* several low-Q L-sections through intermediate resistances (e.g. 10 → 22 → 50 Ω): each step has lower Q, and the ultimate limit is [Bode–Fano](broadband-matching-bode-fano.md).

**Loss with finite component Q.** A series element of reactance $X_s=Q_nR_l$ with unloaded quality $Q_u$ has ESR $X_s/Q_u$; it carries the load current, so it dissipates a fraction $\approx(X_s/Q_u)/R_l=Q_n/Q_u$ of the load power. The shunt element similarly dissipates $Q_n/Q_u$ of it. Hence
$$IL\approx10\log_{10}\!\left(1+\frac{Q_n}{Q_L}+\frac{Q_n}{Q_C}\right)\ \text{dB}.$$
Checked against an exact circuit solve (script): 12.5 → 50 Ω, $Q_L=40$: 0.211 dB exact vs 0.208 estimate; 2 → 50 Ω, $Q_L=30$: 0.747 vs 0.717 dB. This is why matching *very low* impedances (PA transistors, electrically small antennas) is lossy, and why Pi networks with needlessly high Q waste transmitter power. Typical unloaded Q of 0402 parts in the 0.9–2.4 GHz range: multilayer chip inductors ≈ 15–30, wire-wound ≈ 40–70, C0G capacitors 100–500 (read the vendor's Q-vs-frequency curves; a datasheet "Q min 25" is at its test frequency only) — see [inductors at RF](../04-real-components-hf/inductors-at-rf.md) and [capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md).

**Single-stub tuning (Pozar §5.2).** Put a shunt stub a distance $d$ from the load such that the admittance there is $Y_0+jB$, then cancel $jB$ with the stub. With $t=\tan\beta d$:
$$t=\frac{X_L\pm\sqrt{R_L[(Z_0-R_L)^2+X_L^2]/Z_0}}{R_L-Z_0}\ (R_L\neq Z_0),\qquad
B=\frac{R_L^2t-(Z_0-X_Lt)(X_L+Z_0t)}{Z_0[R_L^2+(X_L+Z_0t)^2]},$$
$d/\lambda=\frac{1}{2\pi}\arctan t$ (add ½ if negative); open stub $\ell_o/\lambda=\frac{1}{2\pi}\arctan(-BZ_0)$, short stub $\ell_s/\lambda=\frac{1}{2\pi}\arctan\!\big(1/(BZ_0)\big)$ (add ½ if negative). Two solutions: prefer the one with the shortest $d$ and stub (widest bandwidth). Verified with scikit-rf for $Z_L=60-j80$ Ω.

**Double-stub tuning and its forbidden region (Pozar §5.3).** Two shunt stubs sit at *fixed* positions a distance $d$ apart; only their lengths are adjusted (the principle of lab stub tuners, useful when you cannot move a stub along the line). Normalise admittances to $Y_0$ and let the load (moved, if necessary, along the line to the first stub) be $y=g+jb$ at stub 1. Stub 1 adds $jb_1$, giving $y_1=g+jb'$ with $b'=b+b_1$. The line of length $d$ ($t=\tan\beta d$) transforms it to
$$y_2=\frac{y_1+jt}{1+jty_1}.$$
Stub 2 can cancel any imaginary part, so the only requirement is $\operatorname{Re}y_2=1$. Multiply out: $\operatorname{Re}\{(g+j(b'+t))(1-tb'-jtg)\}=g(1+t^2)$, and $|1+jty_1|^2=(1-tb')^2+t^2g^2$. Setting their ratio to 1,
$$(1-tb')^2=g(1+t^2)-t^2g^2 .$$
A real $b'$ exists only if the right side is non-negative:
$$0\le g\le\frac{1+t^2}{t^2}=\frac{1}{\sin^2\beta d}.$$
Loads with larger conductance at stub 1 lie in the **forbidden region** (a $g$-circle on the Smith chart): for $d=\lambda/8$ or $3\lambda/8$ the limit is $g\le2$; for $d=3\lambda/16$ it is 1.17; as $d\to\lambda/4$ it shrinks to $g\le1$, and $d=\lambda/2$ fails completely, which is why tuners use λ/8 or 3λ/8 spacing. The stub susceptances are
$$b_1=-b+\frac{1\pm\sqrt{(1+t^2)g-t^2g^2}}{t},\qquad b_2=\frac{\pm\sqrt{(1+t^2)g-t^2g^2}+g}{g\,t}$$
(upper signs together); convert each to an open- or short-stub length as for the single stub. Checked (`tools/verify/s6_matching_special.py` §G): a brute-force search over 300 random loads per spacing confirms the boundary, and the closed form for $y=0.4-j0.8$ at λ/8 ($b_1=2.600$, $b_2=3.000$) gives $|S_{11}|=10^{-15}$ in a scikit-rf cascade. **Escaping the forbidden region:** add line between the load and stub 1 — a $g=3$ load at λ/8 spacing becomes $g=0.60$ after λ/8 more line — or use a triple-stub tuner.

**Quarter-wave matching of complex loads.** Insert line until the load rotates onto the real axis: at a voltage maximum $R=Z_0\cdot\text{VSWR}$, at a minimum $R=Z_0/\text{VSWR}$ ([reflections](reflections-vswr-return-loss-mismatch.md)); then add a λ/4 of $\sqrt{Z_0R}$. Alternatively resonate the load reactance with a stub first.

**Multi-section transformers — theory of small reflections.** For $N$ cascaded λ/4 (at $f_0$) sections with small junction reflections $\Gamma_n$ (log form $\Gamma_n\approx\tfrac12\ln(Z_{n+1}/Z_n)$), neglecting multiple reflections,
$$\Gamma(\theta)\approx\sum_{n=0}^{N}\Gamma_ne^{-2jn\theta},\qquad\theta=\beta\ell=\frac\pi2\frac{f}{f_0}.$$
Choosing the $\Gamma_n$ is a filter/polynomial design problem:
- **Binomial (maximally flat)**: $\Gamma(\theta)=A(1+e^{-2j\theta})^N$, i.e. $\ln\frac{Z_{n+1}}{Z_n}=2^{-N}\binom Nn\ln\frac{Z_L}{Z_0}$ (Pozar eq. 5.63), with bandwidth for $|\Gamma|\le\Gamma_m$: $\frac{\Delta f}{f_0}=2-\frac4\pi\arccos\!\left[\frac12\left(\frac{\Gamma_m}{|A|}\right)^{1/N}\right]$, $A=2^{-N}\frac{Z_L-Z_0}{Z_L+Z_0}$.
- **Chebyshev (equiripple)**: $\Gamma(\theta)=Ae^{-jN\theta}T_N(\sec\theta_m\cos\theta)$, with $T_N$ the Chebyshev polynomial, $A=\Gamma_m$, and $\sec\theta_m=\cosh\!\big[\tfrac1N\cosh^{-1}\big(\tfrac{|\ln(Z_L/Z_0)|}{2\Gamma_m}\big)\big]$; bandwidth $\Delta f/f_0=2-4\theta_m/\pi$. Expanding $T_N$ gives the $\Gamma_n$ and hence the section impedances.

**How good is small-reflection theory?** Checked by exact ABCD cascades (script):

| Case | Formula / design | Exact cascade |
|---|---|---|
| Binomial 50→25 Ω, N = 2/3/4, BW for Γ < 0.05 | 50.6 / 71.3 / 85.5 % | 49.1 / 69.7 / 83.9 % |
| Binomial 50→10 Ω, N = 2/3/4 | 35.3 / 55.4 / 70.1 % | 30.4 / 49.0 / 63.6 % |
| Chebyshev 50→25 Ω, N = 2–4, target ripple 0.05 | 0.050 | 0.052 |
| Chebyshev 50→10 Ω, N = 2/3/4, target 0.05 | 0.050 | 0.060 / 0.066 / 0.068 (minimax-refined: 0.0555) |
| Klopfenstein 50→25 Ω, Γm = 0.02 | 0.020 | 0.020 |
| Klopfenstein 50→10 Ω, Γm = 0.02 | 0.020 | 0.026 |

So the theory is excellent at 2:1 but optimistic at 5:1 (the neglected multiple reflections grow with the total mismatch). Exact equal-ripple designs (Riblet/Cohn synthesis, tabulated in Pozar Table 5.2 and in Matthaei, Young & Jones) or a numerical minimax refinement on an exact cascade fix this; the script's refinement shows that for 5:1 over the design band the exact optimum ripple is ≈ 0.0555, i.e. you must accept either 11 % more ripple or slightly less bandwidth.

**Tapered lines.** In the continuous limit $\Gamma(\theta)\approx\frac12\int_0^Le^{-2j\beta z}\frac{d}{dz}\ln\frac{Z(z)}{Z_0}dz$ — a Fourier transform of the taper's log-slope. Exponential taper: $|\Gamma|=|\tfrac12\ln(Z_L/Z_0)\,\mathrm{sinc}(\beta L)|$ (first null at $\beta L=\pi$, i.e. L = λ/2). Triangular: sinc² (lower sidelobes, first null at L = λ). **Klopfenstein (1956)** — the Dolph–Chebyshev taper, optimum in the sense of the shortest taper for a given passband ripple:
$$\ln Z(z)=\tfrac12\ln(Z_0Z_L)+\frac{\Gamma_0}{\cosh A}A^2\phi\!\left(\frac{2z}{L}-1,A\right),\quad \phi(x,A)=\int_0^x\frac{I_1(A\sqrt{1-y^2})}{A\sqrt{1-y^2}}dy,$$
$$\Gamma_0=\tfrac12\ln\frac{Z_L}{Z_0},\quad A=\cosh^{-1}\frac{\Gamma_0}{\Gamma_m},\quad \Gamma(\theta)=\Gamma_0e^{-j\beta L}\frac{\cos\sqrt{(\beta L)^2-A^2}}{\cosh A},$$
passband $\beta L\ge A$. It has small impedance *steps* at both ends (in ln Z each equals $\Gamma_m$; identity $A^2\phi(1,A)=\cosh A-1$ checked). For large ratios the original paper's end values do not meet the terminating impedances, corrected by Kajfez & Prewitt (1973). Our implementation agrees with `skrf.taper.Klopfenstein` to 0.002 in |Γ| (they handle the end step slightly differently).

### Level 3 — what "matched" should mean
- **Conjugate match** maximises power from a fixed linear source (max power transfer theorem, [network theorems](../01-circuit-theory/network-theorems-max-power-transfer.md)); with a lossless network between them, $Z_\text{in}=Z_S^*$ at one plane implies conjugate match at every plane (the mismatch factor is invariant — [Smith chart](smith-chart.md)).
- **PA load**: a transistor PA's output is not a linear source with a fixed internal impedance; its optimum load is set by the voltage/current swing (Cripps load-line, $R_\text{opt}\approx(V_{DD}-V_\text{knee})^2/2P_\text{out}$) and found by load-pull. The matching network transforms 50 Ω to that load, not to the conjugate of the output impedance → [power amplifiers](../06-rf-circuits/power-amplifiers.md).
- **LNA source**: minimum noise figure occurs at $\Gamma_\text{opt}$, generally ≠ $S_{11}^*$; noise match vs gain match trade-off → [LNA design](../06-rf-circuits/lna-design.md).
- **Antennas**: a match only guarantees power *enters* the antenna; small antennas have high Q (Chu limit), so matched bandwidth is fundamentally limited ([Bode–Fano](broadband-matching-bode-fano.md), [small antenna limits](../08-antennas/small-antenna-limits.md)).
- **Real components are not L or C**: a chip inductor has SRF and parallel capacitance; a capacitor has ESL (≈ 0.3–0.6 nH for 0402) and resonates in series. At 2.4 GHz a "33 pF" 0402 capacitor is near series resonance (≈ 0.5 nH gives SRF ≈ 1.2 GHz — above that it is inductive!). Use vendor S-parameter models in simulation ([component models](../04-real-components-hf/component-models-s2p-spice.md)).

## Special topics

### The energy view — what "a matching network just moves the reflection" gets wrong
Take a lossless two-port between a matched source and a load with reflection $\Gamma_L$ (both referenced to $Z_0$). A wave entering the network splits into a part reflected straight back ($S_{11}$) and a part that reaches the load; the load reflects $\Gamma_L$ of it, the network re-reflects $S_{22}$ of that, and so on. Summing the bounces,
$$\Gamma_\text{in}=S_{11}+S_{21}S_{12}\Gamma_L\sum_{n\ge0}(S_{22}\Gamma_L)^n=S_{11}+\frac{S_{21}S_{12}\Gamma_L}{1-S_{22}\Gamma_L}.$$
A match is the condition that this sum is zero: **the network's own reflection and the leak-back of all the internal bounces cancel at the input**. For the 12.5 → 50 Ω L-match at 433 MHz (Example 1) the partial sums of $|\Gamma_\text{in}|$ after 0, 1, 2, 3 and 5 bounces are 0.600, 0.216, 0.078, 0.028, 0.004 → 0. Energy conservation then fixes the rest. The wave arriving at the load is $a_L=S_{21}a_1/(1-S_{22}\Gamma_L)$, and with no loss and no reflected power at the input,
$$|a_L|^2=\frac{P_\text{avail}}{1-|\Gamma_L|^2},\qquad P_L=|a_L|^2(1-|\Gamma_L|^2)=P_\text{avail}.$$
For $\Gamma_L=-0.6$: 1.5625 W travels toward the load and 0.5625 W comes back from it for every watt available, and all 1 W is absorbed. The "reflected" power is not lost or parked: it circulates between the network and the load. The circulating energy is the network's stored energy, and for the L-match $\omega(W_L+W_C)/P_L=Q_n$ exactly (1.732 here; script §A). That is why real matches are lossy in proportion to $Q_n/Q_u$, and narrowband in proportion to $1/Q_n$.

### Negative inductance (or capacitance) in extracted models
A model fitted to measured or simulated S-parameters describes the device *between two chosen reference planes*. If the planes are placed beyond the physical device — you de-embedded more line than was there — the remainder includes a line of negative length, and a short line of length $-\ell$ is, to first order in $\beta\ell$, a T of series $L=-Z_0\ell\sqrt{\varepsilon_\text{eff}}/c$ and shunt $C=-\ell\sqrt{\varepsilon_\text{eff}}/(Z_0c)$. One millimetre too much on JLC-7628 50 Ω microstrip at 2.45 GHz is −0.30 nH and −0.12 pF (ABCD error 3×10⁻³, i.e. $(\beta\ell)^2$-small; script §B). Other sources of negative elements: the T-equivalent of coupled inductors has arms $L_1-M$ that are negative when $M>L_1$ (10 nH and 40 nH at k = 0.8: $L_1-M=-6$ nH), and vendor models sometimes absorb pad or via effects into a negative element. **They are legitimate in simulation** (combine them with the adjacent positive element), cannot be built on their own, and a large one is a hint to re-check the reference planes before trusting the model.

### Using an RF IC's impedance data
Read what the number *is* before matching to it:
- **Input impedance or S11 of a receiver/LNA input** — the impedance the pin presents. Conjugate-match it. Example (illustrative values, not a real part): $S_{11}=0.62\angle{-120°}$ at 915 MHz → $Z_\text{in}=50\frac{1+\Gamma}{1-\Gamma}=15.4-j26.8$ Ω → series +49.85 Ω at the pin (8.67 nH) and shunt +30.0 mS toward the 50 Ω side (5.22 pF) gives exactly 50 Ω.
- **Optimum load $Z_\text{opt}$ (or $Z_L$) of a PA output** — from load-pull: the impedance the network must *present to* the pin. Do not conjugate it. If a datasheet gives $Z_\text{opt}=8+j6$ Ω and you present $8-j6$ Ω by mistake, the error is $|\Gamma|=|Z-Z_\text{opt}|/|Z+Z_\text{opt}^*|=0.6$ (VSWR 4 relative to the intended load) — lost power and linearity. Some vendors tabulate "$Z_\text{source}$/$Z_\text{load}$ seen by the device", others "the device impedance"; the footnote decides.
- **Reference plane and normalisation** — die, package pin or PCB pad; S11 is normalised to 50 Ω unless stated, and a differential S11 to 100 Ω. Rotate the data to your pad with the line between them. For the SX126x/SX127x family, start from the vendor's reference matching network, which already encodes the PA's optimum load ([LoRa reference designs](../15-lora-ism-radios/lora-modules-ebyte-rfm-heltec.md)).

### Differential (balanced) ports — the half-circuit method
A symmetric network driven differentially has a virtual ground on its symmetry plane, so design on the **half circuit**: load $Z_d/2$, source $Z_{s,d}/2$, then map back. **Series elements** of the half circuit appear in each leg with the same value. A **shunt element to (virtual) ground** in the half circuit becomes either two identical elements to real ground, or a single element *across* the pair with **twice the impedance** — a capacitor $C_h$ → $C_h/2$ across, an inductor $L_h$ → $2L_h$ across. Elements to real ground also load the common mode; across-pair elements do not. Example (915 MHz): differential IC input $Z_d=30-j60$ Ω to a 100 Ω differential port (e.g. a 50:100 Ω balun). Half circuit: $15-j30$ Ω to 50 Ω → series $+j52.9$ Ω (**9.20 nH in each leg**) and shunt 5.31 pF to virtual ground → **one 2.66 pF across the pair**. The full network presents 100.000 Ω differential (script §D). Baluns and common-mode behaviour: [baluns](../06-rf-circuits/baluns-and-rf-transformers.md), mixed-mode S-parameters: [S-parameters](s-parameters.md).

### High-impedance detectors
A zero-bias Schottky detector (HSMS-2850 class: $R_s$ ≈ 25 Ω, video resistance $R_v$ ≈ 9.1 kΩ, $C_j$ ≈ 0.18 pF) presents $126.5-j955.6$ Ω at 915 MHz. A broadband 50 Ω shunt resistor in front of it matches the *line* but delivers only 0.54 % of the available power to the junction resistance. A two-element reactive match (shunt B = 0.62 mS across the diode, series +604 Ω) delivers 80 % ideally (the rest is lost in $R_s$) and 60 % with $Q_L$ = 40 inductors — a **20.4 dB sensitivity gain**, with a −3 dB bandwidth of 177 MHz (19 %). The finite inductor Q costs 1.3 dB of the ideal gain. Trade-offs: the match is narrowband and depends on $C_j$ (which varies with drive and temperature), the detector no longer presents 50 Ω outside the band, and in power-measurement use a resistive termination gives flatter, more predictable response ([detectors](../06-rf-circuits/detectors-and-power-meters.md)).

### Interstage matching
Between two transistors neither side is 50 Ω: the driver wants its load-line resistance, the final stage presents a low, reactive input. Match **directly** between the two, not through an imaginary 50 Ω node. Example at 433 MHz: final-stage input $3-j2$ Ω, driver optimum load 25 Ω. Direct L-network: $Q_n=\sqrt{25/3-1}=2.71$, series +10.1 Ω at the gate (3.72 nH, which also absorbs the −j2 Ω) and 39.8 pF shunt at the driver side: **91.4 % efficient (−0.39 dB)** with $Q_L$ = 40, $Q_C$ = 300. Via 50 Ω (3 → 50 Ω, Q 3.96, then 50 → 25 Ω, Q 1): 86.0 % (−0.65 dB) and narrower. Higher-order interstage networks are also where gain flattening, stability resistors and bias feeds are placed ([PA design](../06-rf-circuits/power-amplifiers.md), [stability](../06-rf-circuits/amplifier-stability-and-biasing.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $Q_n=\sqrt{R_h/R_l-1}$; $|X_s|=Q_nR_l$; $|X_p|=R_h/Q_n$ | L-network, real terminations | 12.5→50: Q 1.73 |
| $R_p=R_s(1+Q^2)$, $X_p=X_s(1+Q^2)/Q^2$ | series↔parallel at one f | — |
| Pozar 5.1 closed forms | complex load L-network | two solutions |
| $R_v=R_h/(Q^2+1)$ (Pi), $R_v=R_l(Q^2+1)$ (T) | 3-element networks | Q ≥ Q_n |
| $BW_{RL>10dB}\approx0.5/Q$ | single-stage, Q ≳ 5 | Q 5 → 10 % |
| $IL\approx10\log(1+Q_n/Q_L+Q_n/Q_C)$ | finite-Q components | 5→50 Ω, Q_L 40: 0.36 dB |
| Stub: $t=\tan\beta d$ formula above | shunt single stub | 2 solutions |
| $\ln(Z_{n+1}/Z_n)=2^{-N}\binom Nn\ln(Z_L/Z_0)$ | binomial | accurate for ≤ 2:1 |
| $\Gamma=Ae^{-jN\theta}T_N(\sec\theta_m\cos\theta)$ | Chebyshev | refine for > 3:1 |
| $A=\cosh^{-1}(\Gamma_0/\Gamma_m)$; passband $\beta L\ge A$ | Klopfenstein | 5:1, Γm 0.02: L ≥ 0.70 λ |
| Lumped vs distributed crossover | FR-4 flight computers | < ~1.5 GHz lumped; > ~3 GHz distributed practical |
| $\Gamma_\text{in}=S_{11}+S_{21}S_{12}\Gamma_L/(1-S_{22}\Gamma_L)$; $\lvert a_L\rvert^2=P/(1-\lvert\Gamma_L\rvert^2)$ | lossless matched network | 12.5 Ω load: 1.56 W forward per W |
| $\omega W_\text{stored}/P=Q_n$ | L-network | — |
| Double stub: $g\le1/\sin^2\beta d$ | stub 1 at the load side | λ/8 or 3λ/8 spacing: g ≤ 2 |
| Over-de-embedding by ℓ: $L=-Z_0\ell\sqrt{\varepsilon_\text{eff}}/c$, $C=-\ell\sqrt{\varepsilon_\text{eff}}/(Z_0c)$ | $\beta\ell\ll1$ | 1 mm, 50 Ω, εeff 3.18: −0.30 nH, −0.12 pF |
| Half circuit: series × 1 per leg; shunt $Z_h$ → $2Z_h$ across the pair | symmetric differential network | $C_h$ → $C_h/2$, $L_h$ → $2L_h$ |
| Present $Z_\text{opt}$ (PA); conjugate $Z_\text{in}$ (LNA/receiver input) | datasheet impedance data | wrong choice: \|Γ\| = 0.6 for 8 + j6 Ω |

## Worked examples

### Example 1 — 433 MHz: 12.5 Ω PA-side impedance to 50 Ω
$Q_n=\sqrt{50/12.5-1}=1.732$. Series $X_s=1.732\times12.5=21.65$ Ω → $L=21.65/(2\pi\times433\text{ MHz})=7.96$ nH; shunt $X_p=50/1.732=28.87$ Ω → $C=12.73$ pF (at the 50 Ω side). With a $Q_L=40$ inductor the loss is ≈0.21 dB. Nearest E-series: 8.2 nH, 12 pF — re-check on the Smith chart (the error rotates you off-centre by a few ohms; fine-tune by measurement).

### Example 2 — 433 MHz chip antenna, pi-pad, E-series and finite Q
Measured (at the pi pad, after calibration) $Z_a=32.1-j18.5$ Ω. Since $R<50$: series-then-shunt. Solutions ([Smith chart page](smith-chart.md)): (A) 15.6 nH series + 5.49 pF shunt; (B) 67 pF series + 24.6 nH shunt. Choose (A) (low-pass, inductor value common). With E-series 15 nH + 5.6 pF: RL at 433 MHz = 30.7 dB; adding $Q_L=30$, $Q_C=200$: RL 28.0 dB and the antenna receives 0.954 W of 1 W available (−0.20 dB, almost all in the inductor ESR). Modelling the antenna as a series RLC with Q ≈ 10 around 433 MHz, RL ≥ 10 dB holds over at least 425–441 MHz — comfortably covering the 433.05–434.79 MHz ISM band. (Script section 9d.)

### Example 3 — 915 MHz chip antenna 18 − j35 Ω (902–928 MHz)
$R_L=18<50$: $X=\pm\sqrt{18\times32}+35$ → +59.0 Ω or +11.0 Ω; $B=\pm\frac1{50}\sqrt{32/18}=\pm26.7$ mS.
- Solution A: series +j59 Ω (10.26 nH) then shunt +26.7 mS (4.64 pF) — low-pass; worst RL across 902–928 MHz ≈ 27.8 dB (ideal parts, crude antenna model).
- Solution B: series +j11 Ω (1.91 nH) then shunt −26.7 mS (6.52 nH) — high-pass; worst RL ≈ 32.7 dB. B has lower circulating reactance (smaller series X) → marginally wider and less lossy; A gives some harmonic rejection. For a *receive-only* GNSS-style application B is fine; for the E220 transmitter, A (or B followed by the module's own harmonic filter) is preferable.

### Example 4 — 2450 MHz single stub on JLCPCB 4-layer microstrip
Stackup JLC04161H-7628: L1–L2 prepreg 0.2104 mm, εr 4.4 ([planar lines](planar-lines-microstrip-stripline-cpwg.md)). A 0.36 mm trace gives $Z_0\approx51$ Ω, $\varepsilon_\text{eff}\approx3.15$–3.18, $\lambda_g\approx69$ mm at 2.45 GHz (scikit-rf `MLine` with its default Djordjevic–Svensson dielectric: 51.2 Ω / 3.15; frequency-invariant Hammerstad–Jensen with 35 µm copper: 50.9 Ω / 3.18 — see [planar lines](planar-lines-microstrip-stripline-cpwg.md), where 0.372 mm is the exact bare-board 50 Ω width). For $Z_L=60-j80$ Ω: solution 1: $d=0.1104\lambda_g=7.62$ mm, short stub 0.0950 λg = 6.55 mm (or open stub 23.8 mm); solution 2: $d=17.9$ mm, open stub 0.155 λg = 10.7 mm. Pick solution 1 with the short stub (shortest total, widest band). The via from L1 to the L2 ground plane through 0.21 mm of prepreg is only ≈0.02 nH (Goldfarb–Pucel; ≈0.3 Ω at 2.45 GHz, ≈0.05–0.07 mm of extra stub length; the Johnson & Graham rule of thumb gives ≈0.09 nH, ≈0.3 mm, and over-estimates) — shorten the stub accordingly, mostly for the pad; a through-via to the bottom plane of a 1.6 mm board would be ≈0.54 nH (≈1.8 mm of stub) and matter far more ([PCB parasitics](../04-real-components-hf/pcb-parasitics-traces-vias-pads.md)). Or use solution 2's open stub, subtracting the ≈0.08 mm open-end extension (Hammerstad formula, [stubs page](input-impedance-stubs-quarter-wave.md)).

### Example 5 — broadband 50 → 10 Ω at 2.45 GHz: sections vs taper
λ/4 on the 51 Ω line above ≈ 17 mm (it varies slightly with section width through $\varepsilon_\text{eff}$). For |Γ| ≤ 0.05: binomial N = 3 (40.9, 22.4, 12.2 Ω; ≈ 51 mm) gives 49 % bandwidth (exact); Chebyshev N = 3 (38.3, 22.4, 13.1 Ω) gives ≈ 78 % with 0.066 worst-case ripple (refine to 38.1, 22.4, 13.1 Ω for 0.0555). A Klopfenstein taper at Γm = 0.02 must be at least 0.70 λg long at the *lowest* frequency of interest (≈ 48 mm at 2.45 GHz) and then matches everything above that frequency (high-pass behaviour, until dispersion or radiation intervene) — handy for wideband test fixtures, pointless for a single ISM band. (Exact cascade: expect ≈0.026 rather than 0.020 worst-case for this 5:1 ratio.)

## Practical notes — tuning a pi pad on a real board with a VNA
1. **Design the footprint**: a shunt–series–shunt pad set (0402) right at the antenna/IC feed on a 50 Ω CPWG or microstrip line; populate a 0 Ω (or a DC-block capacitor) in series, leave shunts open for the first measurement. Keep the antenna vendor's ground clearance ([PCB/chip antennas](../08-antennas/pcb-and-chip-antennas.md); layout rules → [13-pcb-rf-layout-emc](../13-pcb-rf-layout-emc/rf-layout-rules.md)).
2. **Measure in the final environment**: assembled board, battery, cables, enclosure — for a rocket, inside the airframe section (fibreglass detunes; carbon fibre blocks) ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).
3. **Put the reference plane at the pad**: solder a short semi-rigid or RG-316 pigtail (shield to board ground right at the pad) and calibrate SOL at its free end, then apply port extension for the pigtail's electrical length; or calibrate at a U.FL with a U.FL cal kit. Otherwise the cable rotates everything ([VNA calibration](../17-test-measurement/vna-fundamentals-calibration.md), [fixtures/de-embedding](../17-test-measurement/fixtures-and-deembedding.md)).
4. **Compute the network**: Smith chart by hand, SimSmith, QucsStudio, or the scikit-rf snippet below; prefer the lower-Q path and E-series values; for transmitters prefer low-pass shapes.
5. **Include parasitics**: use vendor S2P models (Murata, TDK, Johanson, Coilcraft) and pad/trace parasitics in the simulation; a 0 Ω jumper is ≈0.5 nH; the series pad itself adds shunt capacitance to ground.
6. **Populate, re-measure, iterate** (usually 2–3 passes); check the whole band, not a single marker. Check that the match survives hand proximity/airframe movement.
7. **Match ≠ efficiency**: finish with a radiated check (relative received power vs a reference antenna) — a lossy match can look perfect on S11 ([antenna measurement](../08-antennas/antenna-measurement.md)).
8. **RF ICs**: for chips like the SX126x/SX127x, start from the vendor reference-design matching network (it presents the PA's *optimum* load, not a conjugate match) and only retune for layout differences; EBYTE modules already contain this network and present 50 Ω at their pin.

## Common mistakes & misconceptions
- **"Match = cancel the reactance."** Cancelling $X$ leaves $R\neq50$ Ω; you must transform R too (Example 2 on the Smith chart page: cancelling −j18.5 Ω leaves VSWR 1.56).
- **Matching the wrong reference plane** (at the VNA port or U.FL instead of at the antenna pads) — the cable/trace rotates the impedance.
- **Tuning for minimum SWR at the radio through a long lossy cable** — the cable hides the mismatch ([reflections](reflections-vswr-return-loss-mismatch.md)).
- **High-Q Pi networks "for better filtering"** — bandwidth and efficiency drop quickly (Q 12: 3.9 % bandwidth; loss grows ∝ Q/Q_u).
- **Ignoring component Q** — low-R transformations with Q ≈ 20 chip inductors lose ≳ 0.5 dB.
- **Using capacitors above their SRF** — a large 0402 capacitor at 2.4 GHz is an inductor.
- **Trusting small-reflection formulas at large ratios** — verify multi-section/taper designs with an exact cascade.
- **Conjugate matching a PA's small-signal S22** — use the vendor's load or load-pull data.
- **Matching in free air, flying in an airframe** — dielectric loading lowers the resonance by several percent; re-measure installed.
- **Conjugating a load-pull $Z_\text{opt}$** — it is the impedance to present, not the device's own impedance.
- **Matching a differential port with single-ended values** — across-pair shunt elements need twice the half-circuit impedance (half the capacitance, twice the inductance).
- **Deleting a negative element from an extracted model** — it carries a reference-plane offset; fix the planes or keep it.
- **Expecting a double-stub tuner to match anything** — loads with $g>1/\sin^2\beta d$ at the first stub need extra line or a third stub.
- **"The antenna datasheet says 50 Ω."** Only on the vendor's evaluation board with its ground plane; every layout needs its own match.
- **"A matching network just moves the reflection somewhere else."** For a *lossless* network the power bookkeeping is exact: in steady state $P_{load} = P_{inc}(1-|\Gamma_{in}|^2)$, so with $\Gamma_{in}=0$ **all** incident power reaches the load — nothing is "parked" or returned to the source. The load still reflects, but that wave is re-reflected by the network and adds in phase with the forward wave, while the network's own reflection cancels the load's at the input (the same mechanism as a λ/4 transformer or an antireflection coating). What *is* true: between the matching element and the load there are standing waves and higher circulating voltage/current (stored energy ∝ loaded Q), so (i) real components' loss grows with Q ($\approx Q/Q_u$, entry above), (ii) a stub-matched line section still runs at the load's SWR and its line loss rises accordingly ([reflections § loss vs SWR](reflections-vswr-return-loss-mismatch.md)), and (iii) the match is narrowband (Bode–Fano limit, [broadband matching](broadband-matching-bode-fano.md)). (Half-addressed myth from W4-D1, electronics.stackexchange.com/q/676831.)

## How to simulate / verify
- `tools/verify/s6_matching_special.py` — Special topics A–F (bounce series, forward power, stored energy = Q_n; negative-L de-embedding and coupled-inductor T; IC S11 match and the Z_opt-conjugation error; differential half circuit; HSMS-2850-class detector match with finite Q; interstage direct vs via 50 Ω) and §G double-stub (brute-force forbidden region, closed form, scikit-rf cascade). All pass.
- `tools/verify/tline_matching.py` — L-networks (real and complex, both topologies), Pi/T synthesis and bandwidth sweep, finite-Q loss vs estimate, single-stub (vs scikit-rf), binomial and Chebyshev multi-section (formula vs exact cascade + minimax refinement), Klopfenstein (own vs `skrf.taper.Klopfenstein`), and all worked examples. All checks pass.
- scikit-rf: design and sweep an L-network with real parts

```python
import numpy as np, skrf as rf
f = rf.Frequency(400, 470, 141, unit='MHz')
m = rf.media.DefinedGammaZ0(frequency=f, z0=50)
ant = rf.Network('antenna_at_pad.s1p').interpolate(f)        # measured at the pi pad
L = m.inductor(15e-9) ** m.resistor(2*np.pi*433e6*15e-9/30)   # 15 nH, Q ~ 30 (or a vendor .s2p)
C = m.shunt_capacitor(5.6e-12)
matched = C ** L ** ant                                        # source -> shunt C -> series L -> antenna
matched.plot_s_db(); matched.plot_s_smith()
```
- NB: `DefinedGammaZ0` defaults to γ = j rad/m; pass `gamma=1j*2*np.pi*f.f/c` when you use `.line()` for physical lengths (a trap found while writing the script).
- Other tools: SimSmith (free), QucsStudio / Qucs-S, Keysight ADS/Microwave Office (commercial) with optimisation; openEMS for layout-level verification ([16-simulation-tools](../16-simulation-tools/openems-workflow.md)).

## Open questions / gaps
- Exact Chebyshev transformer tables (Riblet synthesis) were not reproduced; the page relies on the numeric minimax refinement instead.
- Q-vs-frequency data for specific 0402 inductor families are quoted as ranges only; exact curves belong to [inductors at RF](../04-real-components-hf/inductors-at-rf.md) / [components](../18-components-parts/rf-transceiver-ics.md).
- Double-stub forbidden region: derived and checked 2026-10-13 (W5-S6). The IC, detector and interstage examples use illustrative or class-typical values, not one specific part's datasheet table.
- PA load-line and LNA noise matching are only previewed (→ 06).

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012 — §5.1 (L-networks, closed forms), §5.2 (single-stub), §5.3 (double-stub), §5.4 (λ/4), §5.5–5.7 (small reflections, binomial eq. 5.63 and bandwidth, Chebyshev, Table 5.2), §5.8 (tapers, Klopfenstein), §5.9 (Bode–Fano). (textbook)
2. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., 1992 — ch. 5 (quarter-wave and multi-section transformers, tapers). (textbook)
3. C. Bowick, *RF Circuit Design*, 2nd ed., Newnes 2008 — ch. 4 (L, Pi, T networks via virtual resistance, Q and bandwidth). (textbook, practical)
4. G. L. Matthaei, L. Young, E. M. T. Jones, *Microwave Filters, Impedance-Matching Networks, and Coupling Structures*, McGraw-Hill 1964 / Artech 1980 — ch. 6 (quarter-wave transformers, exact Chebyshev tables). (textbook)
5. R. W. Klopfenstein, "A transmission line taper of improved design," *Proc. IRE*, vol. 44, pp. 31–35, Jan. 1956, doi:10.1109/JRPROC.1956.274847. (peer-reviewed)
6. D. Kajfez and J. O. Prewitt, "Correction to 'A transmission line taper of improved design'," *IEEE Trans. MTT*, vol. 21, no. 5, p. 364, May 1973, doi:10.1109/TMTT.1973.1128003. (peer-reviewed)
7. S. C. Cripps, *RF Power Amplifiers for Wireless Communications*, 2nd ed., Artech House 2006 — load-line match vs conjugate match. (textbook)
8. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (rev. 2016), chapter "Impedance Matching" — L-sections, stubs, multisection transformers — https://eceweb1.rutgers.edu/~orfanidi/ewa/. (textbook, free)
9. scikit-rf 2.0.1 documentation and source: `skrf.taper.Klopfenstein`, `skrf.media` — https://scikit-rf.readthedocs.io/. (software documentation)
10. Murata LQW15AN / LQG15HS product pages (Q ratings at test frequency, e.g. LQW15AN10NJ00D Q ≥ 25) — https://www.murata.com/ ; distributor listings. (datasheet)
11. Verification: `tools/verify/tline_matching.py`. (numerical check)
12. G. L. Matthaei et al. and D. M. Pozar (above) for the double stub (Pozar §5.3, eqs. for $b_1$, $b_2$ and the forbidden region) — re-derived here. (textbook)
13. Broadcom/Avago HSMS-285x zero-bias Schottky detector diode datasheet — $R_s$ 25 Ω, $C_{j0}$ 0.18 pF, $I_s$ ≈ 3 µA, n ≈ 1.06 (video resistance $nV_T/I_s$ ≈ 9.1 kΩ). (datasheet; values as used elsewhere in the KB)
14. Verification: `tools/verify/s6_matching_special.py` (this KB). (numerical check)
