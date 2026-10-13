---
title: Differential equations for circuits and waves
domain: 00-math-foundations
slug: differential-equations-circuits-waves
tags: [ode, rc, rlc, damping-ratio, natural-frequency, q-factor, resonance, wave-equation, telegrapher, separation-of-variables, helmholtz, waveguide-modes, diffusion, skin-depth]
prerequisites: [complex-numbers-and-phasors.md]
related:
  - laplace-transfer-functions-bode.md
  - vector-calculus-for-em.md
  - special-functions-bessel-sinc.md
  - numerical-methods-overview.md
  - ../01-circuit-theory/transient-and-step-response.md
  - ../01-circuit-theory/resonance-and-q.md
  - ../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md
  - ../02-electromagnetics/wave-equation-plane-waves-polarization.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
  - ../02-electromagnetics/skin-effect-conductor-loss-roughness.md
  - ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Differential equations for circuits and waves

## Questions this page answers
- What is a time constant, and why do we say a capacitor is "charged" after 5τ?
- Why does charging a capacitor from a fixed voltage always waste half the energy, whatever the resistance?
- How do I tell whether an RLC circuit will ring, and how fast the ringing dies?
- What are damping ratio ζ, natural frequency ωₙ and Q, and how are they related?
- Why do my power rails ring after a load step, and how do I damp them?
- Where does the wave equation come from, and why is $f(x-vt)$ a solution?
- How do telegrapher's equations turn into waves on a cable?
- What is separation of variables, and how does it give waveguide modes and cutoff frequencies?
- Why is skin depth a "diffusion" length?

## TL;DR
- **First order** ($\tau\,dy/dt+y=x$): step response $1-e^{-t/\tau}$; 63 % at τ, 95 % at 3τ, 99.3 % at 5τ. RC: τ = RC; RL: τ = L/R.
- Charging a capacitor from a voltage source through *any* resistance dissipates exactly $\tfrac12CV^2$ in the resistance — equal to the energy stored (verified for 1 Ω to 1 MΩ).
- **Second order** $\ddot y+2\zeta\omega_n\dot y+\omega_n^2y=\omega_n^2x$: roots $s=-\zeta\omega_n\pm\omega_n\sqrt{\zeta^2-1}$. Series RLC: $\omega_n=1/\sqrt{LC}$, $\zeta=\frac R2\sqrt{C/L}$, $Q=\frac1R\sqrt{L/C}=1/(2\zeta)$. Underdamped (ζ < 1) rings at $\omega_d=\omega_n\sqrt{1-\zeta^2}$ with envelope $e^{-\zeta\omega_nt}=e^{-Rt/2L}$; critical damping at $R=2\sqrt{L/C}$.
- Ring-down time constant $2Q/\omega_0$ ≈ Q/π cycles: a Q = 50 tank at 433 MHz rings for ~37 ns.
- Decoupling: 5 nH of loop inductance + 100 nF → 7.1 MHz resonance, Q ≈ 22 with 10 mΩ ESR; critical damping would need 0.45 Ω.
- **Wave equation** $\partial_x^2u=\frac{1}{v^2}\partial_t^2u$ follows from telegrapher's equations with $v=1/\sqrt{L'C'}$; general solution $f(x-vt)+g(x+vt)$. Time-harmonic → Helmholtz $\nabla^2u+k^2u=0$.
- **Separation of variables** on bounded regions gives discrete modes: a line or string of length ℓ resonates at $nv/2\ell$; a rectangular waveguide has cutoffs $f_{c,mn}=\frac{c}{2}\sqrt{(m/a)^2+(n/b)^2}$ (WR-90 TE₁₀ = 6.557 GHz).
- Fields inside a good conductor obey a **diffusion** equation → skin depth $\delta=\sqrt{2/(\omega\mu\sigma)}$ (copper: 3.18 µm at 433 MHz).

## Intuition (no math)
A differential equation says "how fast something changes depends on where it is now". A capacitor charging through a resistor charges fast when it's empty (big voltage across the resistor, big current) and slowly as it fills (little voltage left to push current). That self-slowing produces the exponential curve, and τ = RC is the time it would take if it kept its initial rate.

Add an inductor and you get a pendulum: energy swaps between the capacitor's electric field and the inductor's magnetic field, like potential and kinetic energy. Resistance is friction. Little friction → it swings (rings) many times before settling (high Q); a lot → it creeps back without overshoot (overdamped); the boundary is critical damping.

A cable is a long chain of tiny inductors and capacitors. Push charge in at one end and it can't appear at the far end instantly: each little inductor has to get current moving, each capacitor has to charge. The disturbance ripples down the chain at a finite speed — a wave. Because the chain is uniform, the shape of the pulse is preserved as it travels (in the lossless case): that's $f(x-vt)$.

When a wave is trapped between boundaries (a cable open at both ends, a metal waveguide, a cavity), only patterns that "fit" survive — whole numbers of half-waves. Those are the modes, and the lowest one sets the cutoff frequency below which nothing propagates. Separation of variables is the mathematical way of finding those fitting patterns.

## The math

### Level 1 — first-order circuits and exponentials

**RC circuit**, source $V$ switched on at $t=0$, capacitor initially at 0: KVL $V=Ri+v_C$ with $i=C\,dv_C/dt$ gives
$$RC\frac{dv_C}{dt}+v_C=V\ \Rightarrow\ v_C(t)=V\left(1-e^{-t/RC}\right),\quad i(t)=\frac VRe^{-t/RC}.$$

| t/τ | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| fraction reached | 63.2 % | 86.5 % | 95.0 % | 98.2 % | 99.3 % |

10–90 % rise time = 2.2τ. **RL circuit**: τ = L/R; inductor current rises like the capacitor voltage. Discharge is $e^{-t/\tau}$.

**Energy surprise.** Energy delivered by the source: $\int Vi\,dt=CV^2$. Stored in C: $\tfrac12CV^2$. So $\tfrac12CV^2$ is dissipated in R — independent of R (a smaller R just dissipates it faster). Verified numerically for 1 Ω, 1 kΩ and 1 MΩ. Consequences: hot-plug inrush, the "two-capacitor paradox" (connecting a charged C to an uncharged one loses half the energy, in the wire resistance and radiation), and why efficient charging (e.g. of storage caps for pyro channels) uses current-limited or inductive (switching) chargers.

### Level 2 — linear ODEs, second-order systems, resonance

**Linear constant-coefficient ODEs.** $a_ny^{(n)}+\dots+a_1\dot y+a_0y=x(t)$. Solution = homogeneous (natural response) + particular (forced response) [1 §2–4, §10], [2 ch. 2].
- Try $y=e^{st}$ in the homogeneous equation → **characteristic polynomial** $p(s)=a_ns^n+\dots+a_0=0$. Each root $s_k$ gives a mode $e^{s_kt}$ — these are the poles of the transfer function $1/p(s)$ ([Laplace](laplace-transfer-functions-bode.md)).
- **Exponential response formula**: for input $e^{st}$ (including $s=j\omega$), a particular solution is $e^{st}/p(s)$ provided $p(s)\ne0$ [1 §10]. With $s=j\omega$ this *is* phasor analysis: $H(j\omega)=1/p(j\omega)$.
- Constants of the homogeneous part are fixed by initial conditions (capacitor voltages and inductor currents at $t=0^+$, which cannot jump if currents/voltages are finite).

**Series RLC derivation.** KVL: $L\frac{di}{dt}+Ri+\frac1C\int i\,dt=v_s$. Differentiate, or write in terms of the capacitor voltage ($i=C\dot v_C$):
$$LC\,\ddot v_C+RC\,\dot v_C+v_C=v_s\quad\Longleftrightarrow\quad \ddot v_C+2\zeta\omega_n\dot v_C+\omega_n^2v_C=\omega_n^2v_s$$
with $\omega_n=1/\sqrt{LC}$, $2\zeta\omega_n=R/L$ ⇒ $\zeta=\frac R2\sqrt{C/L}$, and $Q=\frac{\omega_nL}{R}=\frac1R\sqrt{\frac LC}=\frac{1}{2\zeta}$ [1 §8, §15]. For a **parallel** RLC the roles invert: $\zeta=\frac{1}{2R}\sqrt{L/C}$, $Q=R\sqrt{C/L}$ (large parallel R = low loss). Characteristic roots:

| Case | Roots | Natural response |
|---|---|---|
| overdamped, ζ > 1 | two real negative | sum of two decaying exponentials, no overshoot |
| critically damped, ζ = 1 ($R=2\sqrt{L/C}$) | double root $-\omega_n$ | $(A+Bt)e^{-\omega_nt}$, fastest without overshoot |
| underdamped, ζ < 1 | $-\zeta\omega_n\pm j\omega_d$, $\omega_d=\omega_n\sqrt{1-\zeta^2}$ | $e^{-\zeta\omega_nt}\cos(\omega_dt+\phi)$ — ringing |
| undamped, ζ = 0 | $\pm j\omega_n$ | sustained oscillation (ideal LC tank) |

Verified by integrating the ODE: measured ringing frequency and decay rate $R/2L$ match for ζ = 0.05 and 0.3. The envelope loses a fraction $2\pi/Q$ of its *energy* per cycle (for high Q); amplitude falls by $e^{-\pi/Q}$ per cycle.

**Forced response and resonance.** Drive with $\cos\omega t$: steady-state amplitude $|H(j\omega)|=1/|p(j\omega)|$ — maximal near $\omega_n$ for light damping; numbers for peak height, peak frequency and overshoot are tabulated on the [Laplace/Bode page](laplace-transfer-functions-bode.md). Verified: the ODE's steady-state current equals $1/|Z|$ from phasors. Resonance is where the stored energy is large compared with energy lost per cycle — the same Q ([resonance and Q](../01-circuit-theory/resonance-and-q.md)).

**State-space form.** Any $n$-th order ODE can be written as $n$ first-order equations $\dot{\mathbf x}=A\mathbf x+B u$ (e.g. $\mathbf x=[v_C,i_L]$). The eigenvalues of $A$ are the poles. This is the form numerical solvers and circuit simulators integrate ([numerical methods](numerical-methods-overview.md), [matrices](matrices-and-linear-algebra-for-networks.md)).

### Level 3 — PDEs: waves, diffusion, separation of variables

**Telegrapher's equations → wave equation.** A line with per-metre inductance $L'$, capacitance $C'$, resistance $R'$, conductance $G'$:
$$\frac{\partial v}{\partial z}=-R'i-L'\frac{\partial i}{\partial t},\qquad\frac{\partial i}{\partial z}=-G'v-C'\frac{\partial v}{\partial t}.$$
Lossless case: differentiate the first in $z$, substitute the second:
$$\frac{\partial^2v}{\partial z^2}=L'C'\frac{\partial^2v}{\partial t^2}\qquad\Rightarrow\qquad v=\frac{1}{\sqrt{L'C'}}.$$
With coax values $L'=258.5$ nH/m, $C'=96.8$ pF/m ([vector calculus](vector-calculus-for-em.md) example 2): $v=2.0\times10^8$ m/s $=c/\sqrt{2.25}$ (verified). Full treatment: [telegrapher equations](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md) [3 §2.1].

**d'Alembert's solution.** For $u_{zz}=u_{tt}/v^2$, any $u=f(z-vt)+g(z+vt)$ works (substitute: both sides give $f''+g''$). $f$ is a forward wave, $g$ a backward (reflected) wave; $v$ is fixed by the medium, the *shape* by the source. Verified with a finite-difference solution: a Gaussian pulse travels 5 m in 25 ns at $2\times10^8$ m/s with its shape unchanged [2 §12.4].

**Lossy lines.** With $R',G'$ the equation gains damping terms (the "telegraph equation"); in phasor form $d^2V/dz^2=\gamma^2V$ with $\gamma=\sqrt{(R'+j\omega L')(G'+j\omega C')}=\alpha+j\beta$. Low-loss: $\alpha\approx\frac{R'}{2Z_0}+\frac{G'Z_0}{2}$ Np/m (verified against the exact square root). Distortionless when $R'/L'=G'/C'$ (Heaviside condition).

**Helmholtz equation.** Assume $e^{j\omega t}$: $\partial_t^2\to-\omega^2$, so the wave equation $\nabla^2u=\frac1{v^2}\partial_t^2u$ becomes $\nabla^2u+k^2u=0$, $k=\omega/v$. Same equation for each Cartesian field component in a source-free uniform medium ([vector calculus](vector-calculus-for-em.md)).

**Separation of variables — rectangular waveguide.** Inside a hollow guide $0<x<a$, $0<y<b$, for fields $\propto e^{-j\beta z}$, the longitudinal field $H_z$ (TE modes) satisfies $(\partial_x^2+\partial_y^2+k_c^2)H_z=0$ with $k_c^2=k^2-\beta^2$. Try $H_z=X(x)Y(y)$: dividing by $XY$ gives $X''/X+Y''/Y=-k_c^2$; each term must be a constant because they depend on different variables. So $X''=-k_x^2X$, $Y''=-k_y^2Y$, with $k_x^2+k_y^2=k_c^2$. Boundary conditions (zero normal derivative of $H_z$ at the walls for TE) force $X=\cos(m\pi x/a)$, $Y=\cos(n\pi y/b)$:
$$k_c=\sqrt{\left(\frac{m\pi}{a}\right)^2+\left(\frac{n\pi}{b}\right)^2},\qquad f_{c,mn}=\frac{c}{2}\sqrt{\left(\frac ma\right)^2+\left(\frac nb\right)^2},\qquad\beta=\sqrt{k^2-k_c^2}.$$
Below $f_c$, $\beta$ is imaginary: the mode is evanescent (decays, doesn't propagate). WR-90 ($a=22.86$, $b=10.16$ mm): TE₁₀ 6.557 GHz, TE₂₀ 13.11 GHz, TE₀₁ 14.75 GHz (verified) — single-mode 8.2–12.4 GHz band [2 §12.3, §12.9], [4]. See [waveguides](../02-electromagnetics/waveguides-and-cavity-resonators.md).
- In **cylindrical** coordinates the radial equation is Bessel's equation → $J_m(k_c\rho)$ (circular waveguide, coax higher-order modes, circular patch antennas).
- In **spherical** coordinates: spherical Bessel functions in $r$ and associated Legendre functions in θ (antenna multipole expansions, spherical near-field scanning). See [special functions](special-functions-bessel-sinc.md).

**Standing waves and cavity modes.** On a lossless line of length ℓ open (or shorted) at both ends, $V(z)\propto\cos(n\pi z/\ell)$ and $f_n=nv/2\ell$: an unterminated 0.5 m cable (velocity factor 0.66) resonates at 198, 396, 594 MHz … — which is why a floating cable on a flight computer can become an efficient antenna near 400 MHz. A line shorted at one end and open at the other: $f_n=(2n-1)v/4\ell$ (quarter-wave resonators; 114 mm of vf-0.66 coax at 433 MHz).

**Diffusion equation and skin depth.** In a good conductor, conduction current dominates displacement current, and Maxwell's curl equations reduce to $\nabla^2\mathbf E=\mu\sigma\,\partial_t\mathbf E$ — a diffusion (heat-type) equation, not a wave equation. Time-harmonic: $\nabla^2E=j\omega\mu\sigma E$, solution $E\propto e^{-(1+j)x/\delta}$ with
$$\delta=\sqrt{\frac{2}{\omega\mu\sigma}}\qquad(\text{copper, }\sigma=5.8\times10^7\text{ S/m: }3.18\ \mu\text{m at 433 MHz},\ 2.18\ \mu\text{m at 915 MHz},\ 1.35\ \mu\text{m at 2.4 GHz}).$$
(Verified.) So RF current flows in a few µm of the surface, and copper roughness of similar size matters ([skin effect](../02-electromagnetics/skin-effect-conductor-loss-roughness.md)). The same diffusion equation governs heat spreading in PA boards ([thermal](../13-pcb-rf-layout-emc/thermal-management-rf.md)).

**Laplace's equation** $\nabla^2V=0$ governs quasi-static fields — e.g. the capacitance per metre of a microstrip or the field between PCB planes. Solved by separation (simple geometries), conformal mapping (Wheeler's microstrip formulas), or numerically by relaxation/finite differences ([numerical methods](numerical-methods-overview.md)).

**PDE types.** Wave (hyperbolic: finite propagation speed), diffusion (parabolic: smoothing, no wavefront), Laplace (elliptic: equilibrium, boundary-value). Numerical schemes and stability conditions differ for each.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| τ = RC; τ = L/R | first order | 10 kΩ × 100 nF = 1 ms |
| $v_C=V(1-e^{-t/\tau})$ | step from 0 | 99.3 % at 5τ |
| $E_{\rm lost}=\tfrac12CV^2$ | charging from a voltage source | independent of R |
| $\omega_n=1/\sqrt{LC}$; $\zeta=\frac R2\sqrt{C/L}$; $Q=\frac1R\sqrt{L/C}$ | series RLC | |
| $\zeta=\frac1{2R}\sqrt{L/C}$; $Q=R\sqrt{C/L}$ | parallel RLC | |
| $R_{\rm crit}=2\sqrt{L/C}$ | series RLC | 5 nH/100 nF → 0.45 Ω |
| ring-down $\tau_{\rm env}=2Q/\omega_0$ | high Q | Q 50 @ 433 MHz → 37 ns |
| $v=1/\sqrt{L'C'}$ | TEM line | coax εr 2.25 → 0.667c |
| $f_n=nv/2\ell$; $(2n-1)v/4\ell$ | open–open; open–short | 0.5 m cable → 198 MHz |
| $f_{c,mn}=\frac c2\sqrt{(m/a)^2+(n/b)^2}$ | rectangular waveguide | WR-90: 6.557 GHz |
| $\delta=\sqrt{2/(\omega\mu\sigma)}$ | good conductor | Cu @ 433 MHz: 3.18 µm |
| $\alpha\approx R'/2Z_0+G'Z_0/2$ | low-loss line | |

## Worked examples

**1. MCU reset / sensor pull-up RC.** 10 kΩ pull-up and 100 nF: τ = 1 ms; the reset line crosses a 0.7·V threshold at $t=-\tau\ln0.3=1.2$ ms. Doubling C doubles it.

**2. Supply rail ringing after a load step.** A LoRa module's PA switches on (hundreds of mA step). The local 100 nF MLCC with ~5 nH of mounting/loop inductance forms a series resonance at 7.1 MHz; with ESR 10 mΩ, Q ≈ 22 — the rail rings for tens of cycles (~$2Q/\omega_0=1$ µs envelope time constant). Critical damping would need ~0.45 Ω of series resistance: in practice add a bulk capacitor with higher ESR (tantalum/polymer) or a small damping resistor/ferrite network, and minimise loop inductance ([decoupling for RF](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md), [ferrites](../04-real-components-hf/ferrites-and-beads.md)).

**3. 433 MHz LC tank.** 10 nH and 13.5 pF resonate at 433 MHz. With a loaded Q of 50 the energy decays with time constant $Q/\omega_0=18$ ns (amplitude $2Q/\omega_0=37$ ns), about 16 cycles per $e$-fold of amplitude. An oscillator built on it needs the active device to supply the ~$2\pi/Q=12.6$ % of stored energy lost each cycle ([oscillators](../05-analog-electronics/oscillators.md)).

**4. Where does the pulse go?** A 1 ns edge launched into 3 m of vf-0.66 coax arrives after 15 ns; if the far end is open it reflects (d'Alembert: the backward wave $g$ is created by the boundary) and returns at 30 ns — the basis of TDR ([TDR](../03-transmission-lines-matching/time-domain-reflectometry.md)).

**5. Accidental antenna.** A 0.5 m unterminated servo or battery lead (vf ≈ 0.66–0.8 depending on insulation and routing) has its first open–open resonance near 200–240 MHz and second near 400–480 MHz — close to 433 MHz. Such cables re-radiate or pick up the telemetry transmitter strongly; ferrite them and keep them short and bundled against ground ([EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md)).

**6. Skin depth and plating.** At 433 MHz copper's δ = 3.18 µm; ENIG's ~3–6 µm nickel layer (ferromagnetic, lower conductivity) is thicker than δ, so RF current flows partly in the nickel, adding loss — one reason RF boards sometimes prefer immersion silver or bare copper with OSP. (Material-specific numbers belong in [JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md).)

## Practical notes
- **Measure ζ from a ringing waveform**: log decrement $\delta_{\log}=\ln(A_n/A_{n+1})=2\pi\zeta/\sqrt{1-\zeta^2}$; $Q\approx\pi/\delta_{\log}$ for high Q.
- **Initial conditions** on real hardware: bulk caps pre-charged by leakage, inductors carrying current at switch-off (flyback spikes $L\,di/dt$ — clamp them).
- **SPICE** `.tran` solves exactly these ODEs; use `.ic` or `uic` to set initial conditions; `.op` finds DC starting points.
- **Wave vs lumped**: treat an interconnect as a transmission line when its delay exceeds ~1/6 of the signal's rise time or its length exceeds ~λ/10 ([quasi-static vs full wave](../02-electromagnetics/quasi-static-vs-full-wave.md)).

## Common mistakes & misconceptions
1. **"A bigger resistor saves energy when charging a capacitor."** No: exactly ½CV² is lost whatever R is; only the time changes.
2. **Mixing series and parallel Q formulas** — series RLC: Q = (1/R)√(L/C) (small R good); parallel: Q = R√(C/L) (large R good).
3. **Expecting phasor answers during transients** — the natural response adds to the forced one until it decays (several τ or $2Q/\omega_0$).
4. **"A capacitor blocks everything above its SRF"** — above self-resonance it's an inductor; the ODE model must include ESL ([capacitors at RF](../04-real-components-hf/capacitors-at-rf-mlcc.md)).
5. **Forgetting the backward wave** $g(x+vt)$ — reflections are part of the general solution, set by boundary conditions.
6. **Treating skin depth as a hard cut-off** — current density decays exponentially; ~63 % of the current is within one δ.
7. **Assuming separation of variables always works** — it needs geometries whose boundaries are coordinate surfaces (rectangles, circles, spheres). Otherwise use numerical methods.
8. **Confusing damping ratio with loss tangent or with Q of a component** — they're related (for a single resonance $Q=1/2\zeta$; for a capacitor $Q_C=1/\tan\delta$) but refer to different things.

## How to simulate / verify
- `python3 tools/verify/math_differential_equations.py` — RC step; ½CV² loss for any R; RLC ringing frequency/decay/Q from ODE integration; critical damping; decoupling resonance; driven steady state vs phasor; finite-difference wave equation (pulse speed/shape); standing-wave modes; telegrapher velocity; WR-90 cutoffs by separation of variables; low-loss α; copper skin depth. All PASS.
- `scipy.integrate.solve_ivp` (use `method='Radau'` or `'LSODA'` for stiff circuits); ngspice/LTspice `.tran`.

## Open questions / gaps
- Nonlinear ODEs (oscillator amplitude limiting, Van der Pol) and describing-function methods are not covered; 05-analog/oscillators should add them.
- Cavity perturbation and coupled-mode theory (for filters and resonators) are left to 02-electromagnetics and 06-rf-circuits.

## Sources
1. H. R. Miller, *18.03 Supplementary Notes*, MIT (2012): §2–4 first-order linear ODEs and sinusoidal solutions, §8 RLC circuits, §10 operators and the exponential response formula, §12 resonance, §15 natural frequency and damping ratio, §20 Fourier series. https://math.mit.edu/classes/18.03/sup/sup0.pdf (lecture notes).
2. E. Kreyszig, *Advanced Engineering Mathematics*, 10th ed., Wiley (2011): ch. 1–2 (first- and second-order ODEs; free/forced oscillations; electric circuits), ch. 12 (PDEs: wave equation, separation of variables, d'Alembert's solution, heat equation, membranes and Bessel functions, Laplacian in cylindrical/spherical coordinates) (textbook; chapter titles ch. 1 "First-Order ODEs", ch. 2 "Second-Order Linear ODEs", ch. 12 "Partial Differential Equations (PDEs)" confirmed from the Wiley India 10th-ed. product page, and §12.4 d'Alembert from an NTNU course plan using the 10th ed. — W5-S18, 2026-10-13; other section numbers not checked).
3. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley (2012), §2.1 lumped-element model of a transmission line (telegrapher equations), §3.3 rectangular waveguide (textbook; section numbers checked by W5-S18 (2026-10-13) against the Wiley 4th-ed. ToC transcribed in gaps/D4-curriculum.md §3.1).
4. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed. (2013), §9.1 waves in one dimension (d'Alembert), §9.4 (absorption and skin depth), §9.5 (guided waves) (textbook).
5. A. V. Oppenheim, A. S. Willsky, *Signals and Systems*, 2nd ed. (1997), §2.4 causal LTI systems described by differential and difference equations (textbook).
