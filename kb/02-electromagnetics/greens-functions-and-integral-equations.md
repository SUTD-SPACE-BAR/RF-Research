---
title: Green's functions and integral equations — scalar and dyadic Green's functions, EFIE/MFIE, Pocklington and Hallén, layered media, the method of moments, equivalence, reciprocity and aperture radiation
domain: 02-electromagnetics
slug: greens-functions-and-integral-equations
tags: [green-function, dyadic-green-function, helmholtz, radiation-condition, efie, mfie, cfie, equivalence-principle, reciprocity, pocklington, hallen, thin-wire, reduced-kernel, method-of-moments, galerkin, point-matching, rwg, sommerfeld-integral, sommerfeld-identity, layered-media, spectral-domain, surface-wave, dcim, sonnet, planar-mom, capacitance, magnetic-current, electric-vector-potential, duality, love-equivalence, schelkunoff-equivalence, physical-optics, uniqueness-theorem, lorentz-reciprocity, reaction, aperture-antenna, aperture-admittance, open-ended-waveguide, babinet, booker-relation, bethe-small-hole]
prerequisites:
  - maxwells-equations.md
  - radiation-from-currents-hertzian-dipole.md
  - ../00-math-foundations/vector-calculus-for-em.md
  - ../00-math-foundations/matrices-and-linear-algebra-for-networks.md
related:
  - near-field-far-field.md
  - boundary-conditions-reflection-refraction.md
  - waveguides-and-cavity-resonators.md
  - ../00-math-foundations/numerical-methods-overview.md
  - ../08-antennas/antenna-simulation-nec-openems.md
  - ../08-antennas/dipoles-and-monopoles.md
  - ../16-simulation-tools/em-solvers-fdtd-mom-fem.md
  - ../16-simulation-tools/nec-antenna-modelling.md
  - ../03-transmission-lines-matching/microstrip-discontinuities.md
  - ../03-transmission-lines-matching/periodic-structures-ebg.md
  - ../08-antennas/horn-reflector-aperture-antennas.md
  - ../13-pcb-rf-layout-emc/shielding-and-isolation.md
level: advanced
confidence: high
last_updated: 2026-10-13
---

# Green's functions and integral equations

## Questions this page answers
- What is a Green's function, and why is exp(−jkR)/(4πR) the one for free space?
- How do I get the field of an *arbitrary* current distribution from the Green's function?
- What is the dyadic Green's function, and how does it contain the Hertzian dipole's near and far fields?
- What are the EFIE and MFIE, and why does the MFIE only work on closed bodies?
- Where do the Pocklington and Hallén equations for wire antennas come from, and what is the "reduced kernel" problem?
- How does the method of moments (NEC, FEKO, my own MoM script) turn an integral equation into a matrix?
- Why do planar EM solvers (Sonnet, Momentum, AXIEM) only mesh the copper, and what are Sommerfeld integrals?
- What are surface-wave poles, and why do they make layered-media Green's functions hard?
- How small must NEC segments be, and why does making them too short break the model?
- What is image theory, and how does it relate to a monopole over a ground plane?
- What is a magnetic current, and why do antenna books use one when no such thing exists?
- What does the equivalence principle actually say, and how does it give the far field of a horn or an open waveguide from the field in its mouth?
- Why is an antenna's receive pattern the same as its transmit pattern, and when does reciprocity fail?
- How much does an open-ended waveguide radiate, and how well is it matched?
- How much RF leaks through a small hole or a slot in a metal enclosure?

## TL;DR
- A **Green's function** is the field produced by a point source. Every linear field problem then becomes an integral: the field of any source is the superposition of point-source fields. For the scalar Helmholtz equation $(\nabla^2+k^2)\psi=-s$ in free space, with $e^{j\omega t}$ and outgoing waves, the Green's function is $g(R)=e^{-jkR}/(4\pi R)$.
- **Vector potential and the dyadic Green's function:** $\mathbf A=\mu\int g\mathbf J\,dV'$ and $\mathbf E=-j\omega\mu\int\bar{\mathbf G}\cdot\mathbf J\,dV'$, with $\bar{\mathbf G}=(\bar{\mathbf I}+\nabla\nabla/k^2)g$, explicitly $g\,[(1-\tfrac{j}{kR}-\tfrac{1}{(kR)^2})\bar{\mathbf I}+(-1+\tfrac{3j}{kR}+\tfrac{3}{(kR)^2})\hat{\mathbf R}\hat{\mathbf R}]$. It reproduces the full Hertzian-dipole fields exactly (sympy, residual 10⁻¹⁷).
- **Integral equations** replace "solve Maxwell everywhere" with "find the surface current that cancels the incident tangential E (EFIE) or H (MFIE) on the metal". **EFIE** works for open and closed metal. **MFIE** only works on closed surfaces, and both fail at the body's internal cavity resonances. The **CFIE** (a weighted sum of the two) is the standard fix.
- **Thin wires.** With the current on the axis and the field matched on the surface (the "reduced kernel"), the EFIE becomes **Pocklington's equation**, $(\partial_z^2+k^2)\int I(z')g\,dz'=-j\omega\varepsilon E_z^{inc}$. Inverting the 1-D operator gives **Hallén's equation**, $\int I(z')g\,dz'=-\tfrac{j}{\eta}[C_1\cos kz+\tfrac V2\sin k|z|]$. The reduced-kernel equation is ill-posed: the solution oscillates or blows up when segments are shorter than about the wire radius.
- **The method of moments (MoM)** expands the current in basis functions, tests the equation with weighting functions, and solves $\mathbf Z\mathbf I=\mathbf V$. The KB's Hallén solver, pulse basis with point matching, gives **80.38 + j45.38 Ω** for a λ/2 dipole with a = 10⁻⁴ λ (Richardson-extrapolated), against **80.21 + j44.96 Ω** from the independent Galerkin MPIE code `ant_mom_wire.py`. The classical 73 + j42.5 Ω is the induced-EMF (assumed sinusoidal current) value.
- **Electrostatic MoM** (Harrington's first example): a 1 m square plate converges to C ≈ 40.8 pF (C/4πε0a = 0.367, within the published 0.36 ± 0.01), first-order in mesh size because of the edge singularity.
- **Layered media.** Over a ground plane or inside a substrate, the Green's function is a **Sommerfeld integral** over transverse wavenumber. It is built from the free-space identity $e^{-jkR}/R=\int_0^\infty J_0(k_\rho\rho)e^{-jk_z|z|}\frac{k_\rho}{jk_z}dk_\rho$ (checked numerically to 10⁻¹⁰) and transmission-line reflection coefficients for each layer. Planar solvers use it so that only the copper is meshed. The difficulty is the **surface-wave pole**: on 1.51 mm FR-4 it sits at β/k0 = 1.00025 at 915 MHz, almost on the branch point k0.
- **Equivalence and reciprocity (Level 3b).** Love's equivalence principle (surface currents $\mathbf J_s=\hat n\times\mathbf H$, $\mathbf M_s=-\hat n\times\mathbf E$) reproduces a dipole's field outside a sphere to 10⁻¹⁴ and gives zero inside; drop $\mathbf M_s$ and the error is 73 %. Lorentz reciprocity, $\int(\mathbf E_1\cdot\mathbf J_2-\mathbf H_1\cdot\mathbf M_2)=\int(\mathbf E_2\cdot\mathbf J_1-\mathbf H_2\cdot\mathbf M_1)$, holds for any linear medium with symmetric ε and μ tensors, loss included; it fails only for magnetised ferrites, plasmas, active and time-varying parts.
- **Aperture radiation.** An aperture in a ground plane radiates exactly like $\mathbf M=-2\hat n\times\mathbf E_a$ in free space; the only approximation is the assumed aperture field. Flanged WR-90 at 10 GHz: **D = 6.31 dBi** (the large-aperture formula $(32/\pi)ab/\lambda^2$ gives 4.20 dBi, 2 dB low for apertures this small), H-plane HPBW 67°, E-plane never 3 dB down; aperture admittance 0.82 + j0.43 → **|Γ| = −12.1 dB**. openEMS approaches these as the flange grows (Dmax 7.41 → 6.96 dBi for 90 → 240 mm flanges).

## Intuition (no math)
Drop a pebble in a pond: ripples spread out in rings. If you know the ripple pattern from one pebble, you know the pattern from a handful of pebbles. Add up one ring pattern per pebble, each centred where that pebble landed and started when it landed. That is all a Green's function is: **the response to a single point source**, which you then add up (integrate) over the actual source. It works because Maxwell's equations are linear.

In free space the "ripple" from a point current is a spherical wave. It gets weaker as 1/distance (so the power spread over a sphere stays constant) and is delayed by distance/c, which is the phase factor $e^{-jkR}$. The radiation page builds the vector potential this way.

**Integral equations** turn the logic round. When a wave hits a metal object, currents flow on the metal, and the field everywhere is "incident field + field radiated by those currents". The currents are exactly those that make the *total* tangential electric field zero on the metal surface. So you do not need to solve for fields in all of space. You only need the unknown current on the metal, which satisfies one equation on the surface. Discretise that current into small patches or segments and you get a matrix equation: **the method of moments**, the engine inside NEC, FEKO and the KB's own wire-antenna scripts.

A microstrip circuit adds a substrate and a ground plane. You can bake them into a cleverer Green's function: the field of a point current *sitting on a grounded dielectric slab*. The solver then only needs unknowns on the copper. That is why Sonnet-type planar solvers are so efficient for PCB filters, and why they cannot handle a finite dielectric block or a radome: those are not in their Green's function.

The **equivalence principle** is the same idea run backwards. Wrap an imaginary bubble round a radiating object. Whatever is inside, the field outside depends only on the tangential fields on the bubble, so you can throw the object away and paint suitable "surface currents" on the bubble instead. That is how a horn's pattern is computed from the field in its mouth, and how openEMS turns near-field data into a far-field pattern. **Reciprocity** says the coupling from antenna 1 to antenna 2 equals the coupling from 2 to 1, which is why an antenna receives best from the directions in which it transmits best.

## The math

### Level 1 — the result and what each symbol means
For a time-harmonic source with $e^{j\omega t}$ in a homogeneous medium (ε, μ; $k=\omega\sqrt{\mu\varepsilon}$ rad/m, $\eta=\sqrt{\mu/\varepsilon}$ Ω):

| Quantity | Formula | Units |
|---|---|---|
| Scalar Green's function | $g(\mathbf r,\mathbf r')=\dfrac{e^{-jkR}}{4\pi R}$, $R=|\mathbf r-\mathbf r'|$ | 1/m |
| Vector potential | $\mathbf A(\mathbf r)=\mu\displaystyle\int_V\mathbf J(\mathbf r')\,g\,dV'$ | Wb/m |
| Electric field | $\mathbf E=-j\omega\mathbf A+\dfrac{\nabla(\nabla\cdot\mathbf A)}{j\omega\mu\varepsilon}=-j\omega\mu\displaystyle\int\bar{\mathbf G}\cdot\mathbf J\,dV'$ | V/m |
| Dyadic Green's function | $\bar{\mathbf G}=\left(\bar{\mathbf I}+\dfrac{\nabla\nabla}{k^2}\right)g$ | 1/m |
| Magnetic field | $\mathbf H=\displaystyle\int\nabla g\times\mathbf J\,dV'$ | A/m |

The *Green's function* is the solution for a unit point source. The *integral* superposes it over the real source. The *integral equation* uses it with an unknown source (the induced current) that is fixed by a boundary condition.

**Level 1½ — the same idea with only algebra.** Think of a wire split into N short pieces, each carrying an unknown current $I_n$.
1. The voltage that piece n induces on piece m is $Z_{mn}I_n$, where $Z_{mn}$ is a *mutual impedance*: a number computed from the Green's function for the distance between the pieces.
2. Every piece must see the applied voltage (only the feed piece has one) cancelled by the sum of induced voltages. That gives N equations, $\sum_nZ_{mn}I_n=V_m$.
3. Solve the N × N linear system and you have the currents. The input impedance is $V_\text{feed}/I_\text{feed}$, and the far field is the sum of each piece's Hertzian-dipole field.

That is the method of moments. Everything below makes the "mutual impedance" precise and says how small the pieces must be.

### Level 2 — derivations

**1. Scalar Green's function.** We want $(\nabla^2+k^2)g=-\delta(\mathbf r-\mathbf r')$. Put the source at the origin and use spherical symmetry. For $R>0$, $\frac{1}{R}\frac{d^2}{dR^2}(Rg)+k^2g=0$, so $Rg=Ae^{-jkR}+Be^{+jkR}$. With $e^{j\omega t}$, $e^{-jkR}$ is an *outgoing* wave, and the Sommerfeld radiation condition $\lim R(\partial_Rg+jkg)=0$ removes B. To fix A, integrate the equation over a small sphere of radius ε. The $k^2g$ term contributes $O(\varepsilon^2)\to0$, and the flux of $\nabla g$ through the sphere is $4\pi\varepsilon^2\partial_Rg\to-4\pi A$. Setting this equal to −1 gives $A=1/(4\pi)$. All three properties (Helmholtz for R > 0, unit delta strength, radiation condition) are confirmed symbolically in `e11_greens.py`. In the physics convention ($e^{-i\omega t}$) the same function is written $e^{+ikR}/(4\pi R)$.

**2. From potentials to the dyadic.** In the Lorenz gauge, $(\nabla^2+k^2)\mathbf A=-\mu\mathbf J$ ([radiation page](radiation-from-currents-hertzian-dipole.md)), so each Cartesian component is a scalar problem: $\mathbf A=\mu\int g\mathbf J\,dV'$. With $\Phi=-\nabla\cdot\mathbf A/(j\omega\mu\varepsilon)$, $\mathbf E=-j\omega\mathbf A-\nabla\Phi=-j\omega\mu\,(\bar{\mathbf I}+\nabla\nabla/k^2)\cdot\int g\mathbf J\,dV'$. Moving the derivatives inside the integral (valid outside the source region) defines $\bar{\mathbf G}$. Writing $\partial_i\partial_jg=g''\hat R_i\hat R_j+(g'/R)(\delta_{ij}-\hat R_i\hat R_j)$, with $g'=-(jk+1/R)g$ and $g''=(-k^2+2jk/R+2/R^2)g$, gives
$$\bar{\mathbf G}=g\left[\Big(1-\frac{j}{kR}-\frac{1}{(kR)^2}\Big)\bar{\mathbf I}+\Big(-1+\frac{3j}{kR}+\frac{3}{(kR)^2}\Big)\hat{\mathbf R}\hat{\mathbf R}\right].$$
The $1/R$ terms are the far field and are transverse: the $\bar{\mathbf I}-\hat{\mathbf R}\hat{\mathbf R}$ projection. The $1/R^2$ and $1/R^3$ terms are the reactive near field. For a current element $\mathbf J=Il\,\hat z\,\delta(\mathbf r')$, this reproduces $E_r$ and $E_\theta$ of the Hertzian dipole exactly (script check 2). Inside the source region $\bar{\mathbf G}$ has a non-integrable $1/R^3$ singularity. It must then be handled as a principal value plus a "depolarisation" term, or avoided by keeping the derivatives outside the integral, which is what the mixed-potential form does.

**3. Surface equivalence and the EFIE / MFIE.** Let an incident field $(\mathbf E^i,\mathbf H^i)$ hit a perfect conductor with surface S and outward normal $\hat n$. The scattered field is radiated by the surface current $\mathbf J_s$ on S. By the equivalence principle, $\mathbf J_s=\hat n\times\mathbf H$, with no magnetic current because $\hat n\times\mathbf E=0$ on PEC.
- **EFIE.** The tangential total E is zero on S:
$$\hat n\times\left[\mathbf E^i-j\omega\mu\int_S\bar{\mathbf G}\cdot\mathbf J_s\,dS'\right]=0\quad\Longleftrightarrow\quad\hat n\times\mathbf E^i=\hat n\times\left[j\omega\mathbf A+\nabla\Phi\right],\ \ \Phi=\frac{1}{\varepsilon}\int_Sg\rho_s\,dS',\ \rho_s=-\frac{\nabla'_s\cdot\mathbf J_s}{j\omega}.$$
The right-hand form is the **mixed-potential EFIE (MPIE)**. It has only a $1/R$ singularity and is what NEC-style wire codes, RWG surface codes and `ant_mom_wire.py` actually discretise. The EFIE is a first-kind equation: the unknown appears only under the integral.
- **MFIE.** Use $\mathbf J_s=\hat n\times\mathbf H$ just outside S. The surface integral's principal value plus its half-residue gives
$$\tfrac12\mathbf J_s(\mathbf r)-\hat n\times\mathrm{PV}\!\int_S\mathbf J_s(\mathbf r')\times\nabla'g\,dS'=\hat n\times\mathbf H^i .$$
This is a second-kind equation (the unknown appears outside the integral too), so it is better conditioned. But the "jump" derivation needs an *inside*, so it only applies to **closed** surfaces. It fails for a dipole, a patch or a plate.
- **Interior resonance.** At frequencies where the closed body's interior would resonate as a cavity, both EFIE and MFIE have non-unique solutions, and the matrix becomes ill-conditioned near those frequencies. For a 100 mm metal box (TE101 at 2.12 GHz) that is inside a typical sweep. The **CFIE** $=\alpha\,\text{EFIE}+(1-\alpha)\eta\,\text{MFIE}$, with α ≈ 0.2–0.5, has no interior resonances.

**4. Pocklington's equation (thin wire).** Consider a straight wire along z with radius $a\ll\lambda$ and length L. Assume an axial current $I(z)$, uniformly distributed round the circumference, with no circumferential current. The tangential E on the surface is then $E_z$. The **reduced (thin-wire) kernel** treats the current as a filament on the axis and observes the field on the surface:
$$g_r(z-z')=\frac{e^{-jkR}}{4\pi R},\qquad R=\sqrt{(z-z')^2+a^2}.$$
$E_z$ from the MPIE is $-j\omega A_z-\partial_z\Phi$, with $\rho=-\frac{1}{j\omega}dI/dz$. Then $E_z^s=\frac{1}{j\omega\varepsilon}(\partial_z^2+k^2)\int I(z')g_r\,dz'$, and setting $E_z^s=-E_z^i$ gives **Pocklington's equation**:
$$\left(\frac{\partial^2}{\partial z^2}+k^2\right)\int_{-L/2}^{L/2}I(z')\,g_r(z-z')\,dz'=-j\omega\varepsilon E_z^i(z).$$
The "exact kernel" instead averages the source over the circumference. It has a logarithmic singularity, and it is what makes very fine segmentation of thick wires well-posed.

**5. Hallén's equation.** Let $\psi(z)=\int I g_r dz'$. Pocklington is then an ODE for ψ: $\psi''+k^2\psi=-j\omega\varepsilon E_z^i$. For a delta-gap source $E_z^i=V\delta(z)$ (V volts across a vanishing gap at the centre), the particular solution follows from $(\partial_z^2+k^2)\frac{\sin k|z|}{2k}=\delta(z)$. With $\omega\varepsilon/k=1/\eta$:
$$\int_{-L/2}^{L/2}I(z')\,g_r(z-z')\,dz'=-\frac{j}{\eta}\left[C_1\cos kz+\frac V2\sin k|z|\right].$$
The free constant $C_1$ (the homogeneous solution; the sine term is absent by symmetry) is fixed by $I(\pm L/2)=0$. Hallén's form has no derivatives of the kernel, so it converges more smoothly with simple pulse bases. Pocklington's form is easier for arbitrary incident fields, which is why scattering codes use it.

**6. The method of moments.** Write the integral equation as $\mathcal L[\mathbf J]=\mathbf E^i_\text{tan}$, with $\mathcal L$ a linear integral operator [1][2].
1. **Expand** $\mathbf J\approx\sum_{n=1}^NI_n\mathbf f_n$ with known basis functions: pulses, triangles (rooftops), sinusoids (NEC) or RWG triangle pairs on surfaces.
2. **Test** by taking the inner product with N weighting functions $\mathbf w_m$: $\sum_nI_n\langle\mathbf w_m,\mathcal L\mathbf f_n\rangle=\langle\mathbf w_m,\mathbf E^i\rangle$, that is $\mathbf Z\mathbf I=\mathbf V$.
3. **Choose the testing.** Point matching ($\mathbf w_m=\delta(\mathbf r-\mathbf r_m)$) is cheapest. Galerkin ($\mathbf w_m=\mathbf f_m$) gives a symmetric $\mathbf Z$ (reciprocity) and stationary (variational) estimates of input impedance.
4. **Fill and solve.** Filling Z costs $O(N^2)$ kernel integrations, with careful singular self-terms. A direct solve is $O(N^3)$; iterative solvers with the fast multipole method scale as $O(N\log N)$.

The electrostatic version, $\int_S\sigma(\mathbf r')/(4\pi\varepsilon_0R)\,dS'=V$ on a conductor, is the simplest MoM. It is how 2-D and 3-D capacitance extractors (and this KB's plate check) work.

**7. Reciprocity (one line, used everywhere; derived with its conditions in Level 3b C).** For two sets of sources in the same linear, isotropic medium, $\int\mathbf E_1\cdot\mathbf J_2\,dV=\int\mathbf E_2\cdot\mathbf J_1\,dV$ (Lorentz). It is why $\bar{\mathbf G}(\mathbf r,\mathbf r')=\bar{\mathbf G}^T(\mathbf r',\mathbf r)$, why Galerkin Z-matrices are symmetric, why $S_{21}=S_{12}$ for passive non-magnetised networks, and why an antenna's transmit and receive patterns are identical.

**8. Image theory — the simplest non-free-space Green's function.** For sources above an infinite PEC plane at z = 0, the Green's function that satisfies the boundary condition is free-space $g$ plus an image term:
- for a *horizontal* current element, the image is reversed: $\bar{\mathbf G}_\text{PEC}\cdot\hat x=\bar{\mathbf G}(\mathbf r,\mathbf r')\cdot\hat x-\bar{\mathbf G}(\mathbf r,\mathbf r'_i)\cdot\hat x$;
- for a *vertical* element, the image has the same sign;
- here $\mathbf r'_i=(x',y',-z')$.

This is exact, and it is why a monopole over a large ground plane has half the impedance of the corresponding dipole. A real (lossy, finite-εr) ground needs the Sommerfeld form of Level 3. The PEC image is its $R=\pm1$ limit.

**9. What MoM error looks like.**

| Error source | Symptom | Fix |
|---|---|---|
| Basis too coarse (h > λ/10) | wrong resonant frequency, low Q | refine; check two meshes |
| Edge singularity of charge/current | first-order convergence (plate: order 0.95) | edge-refined mesh, singular basis, Richardson |
| Delta-gap feed | slow convergence of input susceptance | extrapolate; or use a finite-gap or magnetic-frill feed |
| Reduced kernel with Δz ≲ a | oscillating current, singular Z | longer segments or exact/extended kernel |
| EFIE low-frequency breakdown | ill-conditioning as kh → 0 (the $\nabla\Phi$ term dominates) | loop-star or loop-tree basis, Calderón preconditioning |
| Interior resonance (closed bodies) | spikes near cavity mode frequencies | CFIE |
| Near-singular integrals (close panels) | noisy Z entries | singularity extraction, adaptive quadrature |

### Level 3 — half-space and layered-media Green's functions, and their limits

**Sommerfeld identity (spectral form of the spherical wave).** A spherical wave can be written as a superposition of cylindrical waves in ρ times plane waves in z:
$$\frac{e^{-jkR}}{R}=\int_0^\infty J_0(k_\rho\rho)\,e^{-jk_z|z|}\,\frac{k_\rho}{jk_z}\,dk_\rho,\qquad k_z=\sqrt{k^2-k_\rho^2},\ \operatorname{Im}k_z\le0 .$$
For $k_\rho<k$ the $k_z$ are real (propagating). For $k_\rho>k$ they are imaginary (evanescent), so the integrand decays in |z|. `e11_greens.py` integrates the identity numerically in a slightly lossy medium and matches $e^{-jkR}/R$ to 10⁻¹⁰–10⁻¹⁵ at three (ρ, z) points.

**Half-space (dipole over real ground).** Each spectral plane wave reflects from the interface with the plane-wave Fresnel coefficient $R^{TE}(k_\rho)$ or $R^{TM}(k_\rho)$ ([boundary conditions](boundary-conditions-reflection-refraction.md)). The reflected Green's function is therefore
$$g^r=\frac{1}{4\pi}\int_0^\infty R(k_\rho)\,J_0(k_\rho\rho)\,e^{-jk_z(z+z')}\frac{k_\rho}{jk_z}\,dk_\rho .$$
For a perfect conductor R = ±1 and the integral collapses back to an image source (image theory). For real ground it does not. The leftover is the Norton surface wave and the ground-wave attenuation of [ground-wave propagation](../09-propagation-link-budget/ground-wave-and-lf-mf-propagation.md), and it is what NEC-2's Sommerfeld–Norton option computes for antennas near the ground.

**Layered media (microstrip, stripline, multilayer PCB).** In the spectral domain each layer is a transmission line along z, with characteristic admittance $Y^{TM}=\omega\varepsilon/k_z$ and $Y^{TE}=k_z/(\omega\mu)$. That is the "transverse equivalent network". So the spectral Green's function $\tilde G(k_\rho;z,z')$ of any stack-up is just a cascaded-line voltage or current, computable in closed form. The spatial Green's function is then a Hankel transform (Sommerfeld integral) of $\tilde G$. Three things make these integrals hard:
1. **Branch point** at $k_\rho=k_0$ (the air half-space's $k_z$ goes through zero), plus slow oscillatory decay for large $\rho$.
2. **Surface-wave poles** $k_\rho=\beta_{sw}$ between $k_0$ and $\sqrt{\varepsilon_r}k_0$. For a grounded slab the TM0 pole always exists. On 1.51 mm FR-4 the script finds **β/k0 = 1.000057 / 1.00025 / 1.0018 / 1.011 / 1.037 / 1.39** at 0.433 / 0.915 / 2.45 / 5.8 / 10 / 24 GHz. At UHF the pole almost sits on the branch point, so naive quadrature fails. The TE1 surface wave starts at $c/(4h\sqrt{\varepsilon_r-1})$ = 26.5 GHz, matching the [planar lines](../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md) estimate.
3. **Singular near-field behaviour** as ρ → 0, which must be extracted analytically (the quasi-static images) before numerical integration.

The standard tools are:
- **contour deformation** off the real axis, with residues for the poles;
- the **discrete complex image method (DCIM)**: fit $\tilde G$ by a sum of exponentials, each of which transforms to a "complex image" point source in closed form via the Sommerfeld identity, with the surface-wave poles extracted separately;
- **Sonnet's** approach: put the whole circuit in a shielded metal box. The Green's function becomes a discrete sum over the box's waveguide modes, which converges quickly and is evaluated with FFTs on a uniform cell grid (Rautio & Harrington 1987).

Michalski & Mosig (1997) is the standard reference for the formulations [5].

**Why planar solvers use them.** With the stack-up inside $\bar{\mathbf G}$, the unknowns are only the copper currents (2-D meshes on each layer, plus vertical via currents). The ground planes and laterally infinite dielectrics are exact. This is the "2.5-D" class in [EM solvers](../16-simulation-tools/em-solvers-fdtd-mom-fem.md). The price is that the layers must be laterally uniform and infinite (or box-bounded, for Sonnet). A finite board edge, a component body, a radome or a nose-cone wall are not representable. The surface-wave and radiation losses of [microstrip discontinuities](../03-transmission-lines-matching/microstrip-discontinuities.md) come out automatically, because they are the pole and branch-cut contributions of $\tilde G$.

**Limits of the thin-wire/reduced-kernel model.**
- The reduced-kernel equation has, strictly, no solution: its smooth kernel maps currents to very smooth fields, so a delta-gap field is not in its range. MoM with segments longer than a few radii works because the discretisation regularises it. Shorten the segments below ~a and the solution oscillates or blows up. In the script, for a = λ/100, N = 25 (Δz/a = 2) gives 124 + j40 Ω, while N = 400 (Δz/a = 0.125) gives a singular matrix.
- NEC's guidance (segment length > ~8a for the thin-wire kernel, or use the extended kernel) has the same origin.
- The delta-gap feed has an infinite capacitance in the limit, so the input susceptance converges slowly (first-order: the script's Hallén X falls 68 → 57 → 51 Ω with N = 51 / 101 / 201). Always check convergence, or use Richardson extrapolation.

### Level 3b — magnetic currents, equivalence, reciprocity and aperture radiation

This part supplies the theory that the [horn and aperture](../08-antennas/horn-reflector-aperture-antennas.md), slot and MoM pages use without deriving. Everything is checked in `tools/verify/s5_aperture_equivalence.py`.

**A. Magnetic currents and the electric vector potential F (duality).** Nobody has found magnetic charge, but a fictitious magnetic current density $\mathbf M$ (V/m², or $\mathbf M_s$ in V/m on a surface) is a very useful bookkeeping device. Add it to Faraday's law:
$$\nabla\times\mathbf E=-j\omega\mu\mathbf H-\mathbf M,\qquad\nabla\times\mathbf H=j\omega\varepsilon\mathbf E+\mathbf J .$$
Because the equations are linear, the fields of $\mathbf M$ follow from those of $\mathbf J$ by **duality**: swap $\mathbf E\to\mathbf H$, $\mathbf H\to-\mathbf E$, $\mathbf J\to\mathbf M$, $\mathbf M\to-\mathbf J$, $\varepsilon\leftrightarrow\mu$ (so $\eta\to1/\eta$) and $\mathbf A\to\mathbf F$. The electric vector potential and its fields are
$$\mathbf F=\varepsilon\int\mathbf M\,g\,dV',\qquad\mathbf E_F=-\frac1\varepsilon\nabla\times\mathbf F=-\int\nabla g\times\mathbf M\,dV',\qquad\mathbf H_F=-j\omega\varepsilon\int\bar{\mathbf G}\cdot\mathbf M\,dV' .$$
The total field is the sum of the $\mathbf A$ and $\mathbf F$ parts. Two uses:
- **A small loop is a magnetic dipole.** A loop of area A carrying current I radiates exactly like a magnetic current element $Kl=j\omega\mu IA$ along its axis, in the near and the far field (script §1: a 0.5 mm-radius loop at 433.92 MHz matches to 6.5 × 10⁻⁵, the residual being the loop's finite size, of order $(a/r)^2$).
- **Far-field shortcut.** With the radiation vectors $\mathbf N=\int\mathbf J e^{jk\hat r\cdot\mathbf r'}dS'$ and $\mathbf L=\int\mathbf M e^{jk\hat r\cdot\mathbf r'}dS'$,
$$E_\theta\simeq-\frac{jke^{-jkr}}{4\pi r}\,(L_\phi+\eta N_\theta),\qquad E_\phi\simeq+\frac{jke^{-jkr}}{4\pi r}\,(L_\theta-\eta N_\phi).$$
Every aperture pattern below is one evaluation of these two lines.

**B. Uniqueness and the equivalence principle.** *Uniqueness theorem:* in a region with any loss at all, the field is fixed by the sources inside it plus *either* the tangential E *or* the tangential H on its boundary (Harrington §3-3 [11]). The lossless case is the limit. Consequence: if two source arrangements produce the same tangential fields on a closed surface S, they produce the same field outside S. That licenses replacing a complicated antenna by currents on a surface that surrounds it.

*Love's form.* Keep the true field outside S and set the field inside to zero. The jump in tangential fields across S must be carried by surface currents
$$\mathbf J_s=\hat n\times\mathbf H,\qquad\mathbf M_s=-\hat n\times\mathbf E\qquad(\hat n\text{ pointing outwards}),$$
radiating in the *unbounded homogeneous* medium (the antenna has been removed). Outside they rebuild the original field; inside they cancel each other (the extinction theorem). Script §2 puts the exact fields of a 915 MHz Hertzian dipole on a sphere of radius 0.3λ and integrates the radiation of $\mathbf J_s$ and $\mathbf M_s$ with the full dyadic kernels. The field is reproduced to **5 × 10⁻¹⁵ at 0.8λ and 3λ**, and the field inside is **10⁻¹⁵** of the dipole's. With $\mathbf J_s$ alone the outside field is 73 % wrong: both currents are needed.

*Schelkunoff's forms.* Since the inside field is zero, the inside can be filled with anything without changing the outside field, provided the surface currents stay the same. Fill it with a perfect electric conductor (PEC): an electric current impressed on a PEC surface radiates nothing (it is short-circuited by its own image), so only $\mathbf M_s$ matters, but it now radiates *in the presence of the conductor*. When S is an infinite plane, image theory turns "$\mathbf M_s$ on a PEC plane" into "$2\mathbf M_s$ in free space" (a tangential magnetic current has a same-sign image). Filling with a perfect magnetic conductor (PMC) instead leaves $2\mathbf J_s$.

| Form | Currents used | Exact when | Typical use |
|---|---|---|---|
| Love (free space) | $\mathbf J_s=\hat n\times\mathbf H$, $\mathbf M_s=-\hat n\times\mathbf E$ on a closed S | S closed, true E and H known on it | NF2FF transforms (openEMS, near-field ranges) |
| Schelkunoff, PEC + image | $\mathbf M=-2\hat n\times\mathbf E_a$ over the aperture only | the aperture is in an infinite flat PEC screen and $\mathbf E_a$ is known | slots, flanged guides, horns in a ground plane |
| Physical optics / Huygens source | $\mathbf J_s,\mathbf M_s$ from an assumed aperture field, zero elsewhere, $\mathbf H_a=\hat n\times\mathbf E_a/Z$ | never strictly; good for apertures ≫ λ | unflanged horns, reflector apertures (the obliquity factor $(1+\cos\theta)/2$) |

The **principle is exact**. The approximation in every practical aperture calculation is the *assumed aperture field* (usually the incident waveguide mode), plus, for the physical-optics form, the assumption that the fields outside the aperture are zero.

**C. Lorentz reciprocity and the reaction.** Let sources 1 ($\mathbf J_1,\mathbf M_1$) produce $\mathbf E_1,\mathbf H_1$ and sources 2 produce $\mathbf E_2,\mathbf H_2$, at the same frequency in the same medium. Expand with $\nabla\cdot(\mathbf a\times\mathbf b)=\mathbf b\cdot\nabla\times\mathbf a-\mathbf a\cdot\nabla\times\mathbf b$ and the two curl equations:
$$\nabla\cdot(\mathbf E_1\times\mathbf H_2-\mathbf E_2\times\mathbf H_1)=\mathbf E_2\cdot\mathbf J_1-\mathbf E_1\cdot\mathbf J_2+\mathbf H_1\cdot\mathbf M_2-\mathbf H_2\cdot\mathbf M_1 .$$
The terms $j\omega\mu\mathbf H_1\cdot\mathbf H_2$ and $j\omega\varepsilon\mathbf E_1\cdot\mathbf E_2$ cancelled. That cancellation is the whole condition: it needs **ε and μ to be symmetric tensors** (scalars, or anisotropic but symmetric). Integrate over all space; the surface term vanishes at infinity by the radiation condition (or on any PEC/PMC/impedance boundary). The result is Rumsey's **reaction theorem**:
$$\langle1,2\rangle\equiv\int(\mathbf E_1\cdot\mathbf J_2-\mathbf H_1\cdot\mathbf M_2)\,dV=\int(\mathbf E_2\cdot\mathbf J_1-\mathbf H_2\cdot\mathbf M_1)\,dV\equiv\langle2,1\rangle .$$
Script §4 checks it for 20 random dipole pairs in free space and over a PEC ground (relative difference 10⁻¹⁵), and for an electric source against a magnetic source.
- **What it allows:** any inhomogeneity, any loss (σ is part of a complex scalar ε), any boundary that is itself reciprocal.
- **What breaks it:** magnetised ferrites and plasmas (the ionosphere, with the Earth's field) have *antisymmetric* off-diagonal ε or μ (gyrotropy). Active devices, non-linear and time-varying parts also break it. That is why an isolator or circulator needs a biased ferrite, and why an ideal gyrator has $S_{21}=-S_{12}$ (script).
- **Consequences used across the KB:** $Z_{12}=Z_{21}$ and $S_{12}=S_{21}$ for passive, unbiased networks (equal reference impedances); identical transmit and receive patterns; the effective aperture $A_e=G\lambda^2/4\pi$ (reciprocity plus a thermal-equilibrium argument); symmetric Galerkin MoM matrices; and the induced-EMF mutual impedance $Z_{21}=-\frac{1}{I_1I_2}\int\mathbf E_1\cdot\mathbf J_2\,dV$ used in [dipoles](../08-antennas/dipoles-and-monopoles.md).
- **What it does not say:** that a *link* is symmetric. Path loss and antenna gains are reciprocal, but transmit powers, noise figures, antenna noise temperatures and local interference are not. See the two-direction budget in [ground-station design](../15-lora-ism-radios/ground-station-design.md#link-asymmetry-and-receiver-overload-near-the-pad).

**D. A rectangular aperture in a ground plane (open-ended, flanged waveguide).** Take the TE10 mode in the mouth of a guide (a along x, b along y, centred on the origin) opening into an infinite PEC flange at z = 0: $\mathbf E_a=\hat y\,E_0\cos(\pi x/a)$. Schelkunoff plus image gives $\mathbf M=-2\hat z\times\mathbf E_a=2E_0\cos(\pi x/a)\,\hat x$ radiating in free space. The radiation vector is a product of two 1-D Fourier integrals:
$$L_x=2E_0\cdot\frac{\pi a}{2}\,\frac{\cos X}{(\pi/2)^2-X^2}\cdot b\,\frac{\sin Y}{Y},\qquad X=\tfrac{ka}{2}\sin\theta\cos\phi,\quad Y=\tfrac{kb}{2}\sin\theta\sin\phi .$$
With $L_\theta=L_x\cos\theta\cos\phi$ and $L_\phi=-L_x\sin\phi$:
- **E-plane** (φ = 90°, the plane containing $\mathbf E_a$): $E_\theta\propto\sin Y/Y$, with **no obliquity factor**. Because b = 0.34λ for WR-90 at 10 GHz, the E-plane pattern is only −1.7 dB at grazing: it never reaches −3 dB.
- **H-plane** (φ = 0): $E_\phi\propto\cos\theta\,\cos X/((\pi/2)^2-X^2)$. HPBW **66.6°**, −9.8 dB at 60°.
- **Directivity** by integrating $|E|^2$ over the half-space: **D = 4.27 = 6.31 dBi**. The textbook result $D=(32/\pi)ab/\lambda^2$ (4.20 dBi here) assumes the radiated power equals $\int|E_a|^2/2\eta\,dS$, which holds only for apertures much larger than λ. It is **2.1 dB low** for WR-90, and converges to the integral for a 10λ × 5λ aperture (27.07 vs 27.09 dBi). Other guides: WR-430 at 2.45 GHz 7.08 dBi (formula 6.08), WR-42 at 24 GHz 6.54 dBi (formula 4.78).
- **Aperture admittance (variational).** Assume the same aperture field and equate the complex power that $2\mathbf M$ sends into the half-space to $\tfrac12|V|^2Y_{ap}$, with the modal normalisation of [waveguides](waveguides-and-cavity-resonators.md). The spectral form is $P=\frac{1}{16\pi^2\eta k}\iint\frac{k^2-k_x^2}{k_z}|\tilde K_x|^2dk_xdk_y$, with $\tilde K_x$ the Fourier transform of $2E_y$: the visible region $k_\rho<k$ gives the conductance, the evanescent region the susceptance. Normalised to the TE10 admittance: **y = 0.816 + j0.426 at 10 GHz, |Γ| = 0.249 (−12.1 dB)**; −12.1 dB at 8.2 GHz and −13.6 dB at 12.4 GHz. This single-mode Galerkin estimate is stationary, so it is better than the assumed field it uses.

*Check against a full-wave model (openEMS).* `s5_aperture_openems.py` models a real WR-90 ending in a square PEC flange of side F (TE10 port, PML, NF2FF box). Pre-registered tolerances (written before running): H-plane within 1 dB to 60°, E-plane within 2 dB to 45°, Dmax within 1 dB of the infinite-flange model.

| Flange F | Mesh | Dmax (dBi) | max E-plane dev. (≤ 45°) | max H-plane dev. (≤ 60°) | \|S11\| at 10 GHz |
|---|---|---|---|---|---|
| 90 mm (3λ) | λ/20 | 7.41 | 1.81 dB | 2.64 dB | −10.7 dB |
| 90 mm | λ/30 | 7.44 | 1.87 dB | 2.42 dB | −11.8 dB |
| 150 mm (5λ) | λ/20 | 7.12 | 1.45 dB | 1.64 dB | −10.7 dB |
| 240 mm (8λ, not pre-registered) | λ/20 | 6.96 | 0.97 dB | 0.95 dB | −10.7 dB |
| infinite (equivalence model) | — | **6.31** | 0 | 0 | −12.1 dB (variational) |

The pre-registered tolerances **failed** for the 90 and 150 mm flanges and were met only by the 240 mm flange. The cause is the finite flange, not the principle. The E-plane aperture field still has 1.7 dB of strength at grazing incidence, so it lights the flange edges and their diffraction ripples the pattern and narrows the beam. The deviation shrinks steadily with F, while the λ/30 mesh changes Dmax by only 0.03 dB. Part of the remaining +0.65 dB in Dmax is the NF2FF box having no back face (power radiated behind the flange is not counted). The reflection coefficient moves towards the variational −12.1 dB as the mesh is refined. **Lesson for builders:** a "flange" only behaves as an infinite ground plane for pattern purposes when it is several wavelengths across; a 3λ plate still changes the gain by 1 dB.

**E. Babinet, slots and small holes.**
- **Booker's relation.** A slot in an infinite thin screen and the complementary flat dipole satisfy $Z_\text{slot}Z_\text{dipole}=\eta_0^2/4$. A half-wave slot is therefore $\eta_0^2/(4\times(73.1+j42.5))$ = **363 − j211 Ω**, which is why slots are fed off-centre or by a microstrip crossing. A **seam or slot in an enclosure approaching λ/2 is a resonant antenna**, not a small leak: 61 mm at 2.45 GHz, 164 mm at 915 MHz.
- **Bethe's small hole.** A circular hole of radius $r\ll\lambda$ in a thin screen re-radiates like an electric dipole $\propto(2r^3/3)E_n$ plus a magnetic dipole $\propto(4r^3/3)H_t$ (the polarisabilities), each driven by the field that would exist at the screen without the hole. For normal incidence only the magnetic term acts. Imaged on the shadow side, it gives a transmission cross-section $\sigma=\frac{64}{27\pi}k^4r^6$, re-derived in script §5. Relative to the hole's area, the transmission falls as $(kr)^4$: a 3 mm hole passes **−81 / −68 / −51 dB** at 433 / 915 / 2450 MHz, a 10 mm hole −60 / −47 / −30 dB. Holes are cheap; slots and seams are expensive (see [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md) and the deep-hole cutoff rule in [waveguides](waveguides-and-cavity-resonators.md)).

## Design equations & rules of thumb

| Equation / rule | When valid | Typical value / note |
|---|---|---|
| $g=e^{-jkR}/(4\pi R)$ | homogeneous, unbounded medium, $e^{j\omega t}$ | physics convention: $e^{+ikR}$ |
| $\bar{\mathbf G}$ explicit form above | outside the source | near field: $1/(kR)^3$ terms dominate for kR < 1 |
| EFIE (MPIE) | open or closed PEC | first kind; condition number grows as mesh refines |
| MFIE | closed PEC only | second kind; fails for plates, wires |
| CFIE, α ≈ 0.2–0.5 | closed bodies across interior resonances | fixes non-uniqueness |
| Pocklington / Hallén, reduced kernel | $a\ll\lambda$, segment Δz ≳ 2–8a | λ/2, a = 10⁻⁴λ: 80.2 + j45.0 Ω (exact half-wave length) |
| Induced-EMF λ/2 dipole | sinusoidal current assumption | 73.1 + j42.5 Ω |
| MoM cost | dense Z | fill $O(N^2)$, LU $O(N^3)$, MLFMM $O(N\log N)$ |
| Square plate C | 1 m side, isolated | ≈ 40.1–40.8 pF (C/4πε0a ≈ 0.36) |
| Sommerfeld identity | any ρ, z | the bridge to layered media |
| Grounded-slab TM0 pole | always present | β ≈ k0(1 + small) at UHF |
| TE1 onset $c/(4h\sqrt{\varepsilon_r-1})$ | grounded slab | 26.5 GHz for 1.51 mm FR-4 |
| Love equivalence $\mathbf J_s=\hat n\times\mathbf H$, $\mathbf M_s=-\hat n\times\mathbf E$ | closed S, homogeneous outside | exact (script: 10⁻¹⁴) |
| Aperture in a ground plane: $\mathbf M=-2\hat n\times\mathbf E_a$ in free space | infinite flat PEC flange | error = error of the assumed $\mathbf E_a$ |
| Small loop ≡ magnetic dipole $Kl=j\omega\mu IA$ | loop ≪ λ | all field terms |
| Reaction $\langle1,2\rangle=\langle2,1\rangle$ | symmetric ε, μ (loss allowed) | fails: ferrite, plasma, active |
| TE10 flanged aperture D | integrate the pattern; $(32/\pi)ab/\lambda^2$ only for a, b ≫ λ | WR-90 10 GHz: 6.31 dBi (formula 4.20) |
| Flanged WR-90 admittance | single-mode variational | 0.82 + j0.43, \|Γ\| −12.1 dB |
| Booker $Z_\text{slot}Z_\text{dip}=\eta_0^2/4$ | thin infinite screen | λ/2 slot ≈ 363 − j211 Ω |
| Bethe hole $\sigma=\frac{64}{27\pi}k^4r^6$ | $kr\ll1$, thin screen, normal incidence | 3 mm, 2.45 GHz: −51 dB of its area |

## Worked examples

### Example 1 — the field of a 433 MHz current element from the dyadic Green's function
Take I·l = 1 mA × 10 mm = 10⁻⁵ A·m at 433 MHz (k = 9.07 rad/m) and observe at R = 0.5 m broadside (θ = 90°, kR = 4.54). Then $\hat{\mathbf R}\hat{\mathbf R}\cdot\hat z=0$, so only the $\bar{\mathbf I}$ term acts: $E_z=-j\omega\mu Il\,g\,(1-\frac{j}{kR}-\frac{1}{(kR)^2})$.
- **Magnitude prefactor:** $\omega\mu Il\,|g|$ = (2π·433e6)(4π×10⁻⁷)(10⁻⁵)/(4π·0.5) = 5.44×10⁻³ V/m.
- **Bracket:** 1 − 0.0485 − j0.220, magnitude 0.976.

So |E| = **5.3 mV/m**, only 2.4 % below the far-field value, because at kR = 4.5 the near-field terms are already small. At R = 5 cm (kR = 0.45) the bracket becomes 1 − 4.9 − j2.2, magnitude 4.5, and the near field dominates. This is the same physics as the [near-field page](near-field-far-field.md), from a different route.

### Example 2 — capacitance of a square plate by MoM, step by step
Split a 1 m plate into 12 × 12 squares. Unknown $\sigma_n$ is the uniform charge density on cell n. Point-match V = 1 V at the cell centres, using the exact potential of a uniformly charged square (a closed-form panel integral). Solve the 144 × 144 system and sum $\sigma_nA_n$:
- 12 × 12 gives C = **39.71 pF**; 24 × 24 gives 40.24 pF; 48 × 48 gives 40.52 pF.
- Observed order ≈ 0.95 (the charge has a $\rho^{-1/2}$ edge singularity), and Richardson extrapolation gives **40.82 pF** (C/4πε0a = 0.367).

The commonly quoted converged value is about 0.3607 (from knowledge). Our first-order extrapolation is 1.7 % high, which shows why edge-refined meshes or singular basis functions matter in capacitance extraction. For comparison, a disc of the same area has C = 8ε0r with r = 0.564 m, giving 39.96 pF.

### Example 3 — Hallén solution for a 433 MHz dipole made of 1 mm-radius wire
At 433 MHz, λ = 692 mm and a/λ = 1.44×10⁻³, close to the script's 10⁻³ λ case. For an exact λ/2 dipole the script's Hallén (pulse, point-matched, extrapolated) gives **87.8 + j47.6 Ω** and the Galerkin MPIE gives 86.1 + j46.2 Ω (60 segments, about 2 % apart, both still converging). The +j47 Ω is why a real half-wave dipole is cut **4–6 % short** to resonate: [dipoles](../08-antennas/dipoles-and-monopoles.md) gives L_res = 0.4757 λ for a/λ = 10⁻³, at R ≈ 72 Ω. With 0.5 mm wire and 1 mm segments (Δz/a = 2), the reduced kernel is still fine. Do not push NEC below about 8 radii per segment without the extended kernel.

### Example 4 — why a planar solver struggles at 433 MHz on a 1.5 mm board
The TM0 pole sits at β = 1.000057 k0 at 433 MHz. The spectral integrand has a pole 0.006 % above the branch point. A naive real-axis quadrature therefore needs enormous resolution there, or the pole must be extracted analytically. A shielded-box code like Sonnet sidesteps this, because a box has no continuous spectrum. The cost is that the box walls must be far enough away, or deliberately part of the model. The box's own cavity modes must also be kept out of band. For a 100 × 100 mm box the TE101 mode is at 2.12 GHz in air (lower with substrate loading). That is a real trap when simulating 2.4 GHz layouts in a box sized like the PCB.

### Example 5 — a 915 MHz monopole on the av-bay bulkhead, via image theory
A λ/4 whip (82 mm) over an infinite ground plane is, by image theory, half of a λ/2 dipole. Its input impedance is half the dipole's: about 36.5 + j21 Ω for the induced-EMF current, or 40 + j22 Ω from a converged MoM at a = 10⁻⁴ λ, before trimming for resonance. On a real 100 mm aluminium bulkhead (0.3 λ across at 915 MHz) the image is incomplete. Current flows onto the airframe, and the impedance and pattern move. That is the case where a full MoM model of the whip plus the plate (`ant_mom_general.py` with a wire-grid plate, or openEMS) is needed, as in [antennas on rockets](../08-antennas/antennas-on-rockets.md).

### Example 6 — an open-ended WR-90 as a 10 GHz radar test antenna
A WR-90 guide with a 100 × 100 mm plate soldered round its mouth is a common bench antenna for 10 GHz Doppler modules. From Level 3b D: with an infinite flange D = 6.3 dBi, H-plane HPBW 67°, an E-plane pattern almost flat to ±90°, and |Γ| ≈ −12 dB (mismatch loss $-10\log(1-0.249^2)$ = 0.28 dB). With a 3λ plate expect about 1 dB more peak directivity (openEMS 7.4 dBi) and E-plane ripple of ±1–2 dB from the plate edges. For a two-way radar link budget at 1 m, the 1 dB plate effect counts twice, so measure the plate you actually built or use a standard-gain horn ([horn page](../08-antennas/horn-reflector-aperture-antennas.md)).

### Example 7 — vent holes and a seam in an av-bay lid at 2.45 GHz and 433 MHz
An aluminium lid has twelve 3 mm vent holes and a 60 mm unsealed seam. Each hole transmits $\sigma=\pi r^2\times10^{-5.07}$ at 2.45 GHz, i.e. 6 × 10⁻¹¹ m² (scaled from the −51 dB figure). The twelve together are −40 dB of one 3 mm hole's area: negligible. The seam is 0.49λ long at 2.45 GHz, so it is a resonant slot antenna: by Booker it has an impedance of order 400 Ω and couples strongly to the internal fields. At 433 MHz the same seam is 0.087λ and leaks little, but 433 MHz harmonics at 2.17 and 2.6 GHz will find it. Fix: close seams with screws spaced < λ/20 at the highest harmonic of concern (6 mm at 2.45 GHz) or conductive gasket; the holes can stay.

### Example 8 — using reciprocity to measure a rocket antenna pattern
To measure the pattern of the airframe's 433 MHz antenna you may transmit from a fixed ground-station Yagi and record RSSI on the rocket's own radio as you rotate the airframe. Reciprocity guarantees the receive pattern equals the transmit pattern. It fails for an **active** antenna (a GNSS patch with an integrated LNA): that is a non-reciprocal device, so measure it in the direction it is used (receive), with the LNA powered. Reciprocity also does not make the RSSI the same at both ends of the link: the E22 transmits 33 dBm and the ground station perhaps 20 dBm, and their receivers have different noise figures.

## Practical notes
- **Wire antennas** (dipoles, Yagis, helices): MoM is the right tool. Use NEC-2 via PyNEC, or the KB's own `ant_mom_wire.py` (parallel wires) and `ant_mom_general.py` (junctions, loads, ground). See [antenna simulation](../08-antennas/antenna-simulation-nec-openems.md) and [NEC modelling](../16-simulation-tools/nec-antenna-modelling.md). Keep segment length between ~λ/50 and λ/10, and above ~8 wire radii.
- **PCB circuits** (filters, couplers, discontinuities): 2.5-D MoM with layered Green's functions is efficient, but needs laterally uniform stack-ups. openEMS (FDTD) meshes everything and handles finite boards and enclosures.
- **Ground effects for ground-station antennas**: NEC's Sommerfeld–Norton ground matters for antennas within ~0.1–0.2 λ of real ground. For a 433 MHz Yagi on a 1.5 m mast (2.2 λ), the reflection-coefficient approximation is fine.
- **Interior resonance** shows up as sharp, unphysical spikes in a MoM sweep of a closed metal enclosure. Switch on the CFIE option (FEKO, Gmsh-based codes), or treat any resonance near the box's TE101 frequency with suspicion.

- **Radome and nose-cone problems** (dielectric shells around an antenna) fit neither wire MoM nor planar MoM. Use FDTD (openEMS) or FEM, or a volume- or surface-integral formulation for dielectrics (PMCHWT) in commercial codes. For thin walls, the plane-wave slab estimate in [boundary conditions](boundary-conditions-reflection-refraction.md) is often enough.
- **Cost check before you start:** a surface MoM with N unknowns needs 16N² bytes of complex double storage. N = 10 000 is 1.6 GB, and LU then takes minutes. A 2.4 GHz patch array on a 10 × 10 cm board at λ/20 meshing is ~10⁴ unknowns. A whole rocket at 2.4 GHz is not feasible without MLFMM.

## Common mistakes & misconceptions
- **Believing a MoM answer without a convergence check.** The KB's Hallén reactance moved 68 → 57 → 51 Ω as N doubled twice. One mesh is not a result.
- **Using a wire-grid model of a solid plate with too coarse a grid.** The grid spacing must be ≲ λ/10, and the wire radius should be chosen so that the total wire surface equals the plate's area per side (the "equal-area rule").
- **Mixing time conventions.** Physics texts use $e^{-i\omega t}$ and $e^{+ikR}$. Copying a Green's function from one convention into a code using the other gives incoming waves and negative radiation resistance.
- **"The Green's function is the field."** It is the field of a *unit point* source. The actual field is its integral against the source, including the vector and dyadic structure.
- **Using the MFIE on an open structure** (a patch, plate or dipole). It has no interior, so the equation is meaningless.
- **Refining a thin-wire mesh below the wire radius** "for accuracy" makes the reduced-kernel solution worse, not better.
- **Expecting 73 Ω from a MoM model of an exact λ/2 dipole.** 73 + j42.5 Ω is the induced-EMF approximation. A converged MoM with a = 10⁻⁴ λ gives about 80 + j45 Ω for the same length, and resonance needs a shorter dipole.
- **Thinking planar MoM models the PCB edge.** Infinite-substrate Green's functions have no edges. Board-edge radiation and finite-ground effects need FDTD, FEM or a full 3-D MoM with dielectric volumes.
- **"The equivalence principle is an approximation."** It is exact. The approximations are the assumed aperture field (usually the bare incident mode) and, in the physical-optics form, setting the fields outside the aperture to zero.
- **Using $\mathbf J_s$ alone (or forgetting the image factor 2 for $\mathbf M$ over a ground plane).** Love's form needs both currents (73 % error with one). Over a PEC plane only $\mathbf M$ is used, but doubled, radiating in free space.
- **Quoting $(32/\pi)ab/\lambda^2$ for an open waveguide.** It is a large-aperture formula and is 2 dB low for WR-90 at 10 GHz. Integrate the pattern.
- **"A 3λ plate is an infinite ground plane."** For an aperture whose E-plane field is strong at grazing, the plate edges change the peak gain by about 1 dB and ripple the pattern.
- **"Reciprocity fails in lossy media."** Loss is allowed. Reciprocity needs symmetric ε and μ tensors; magnetised ferrites and plasmas break it, as do amplifiers.
- **"Reciprocity means both ends of my link see the same SNR."** Only the path is reciprocal; powers, noise figures and local noise are not.
- **Treating a slot like a small hole.** Bethe's $(kr)^4$ law holds for $kr\ll1$. A slot of length near λ/2 is a resonant antenna (Booker), however narrow it is.
- **Treating DCIM output as exact.** Its exponential fits can miss surface-wave behaviour at large ρ unless the poles are extracted.

## How to simulate / verify
- `python3 tools/verify/e11_greens.py` (≈ 2 s): **15/15 checks**. It covers the Helmholtz equation, delta strength and radiation condition for g (sympy); dyadic G = Hertzian-dipole fields and the explicit dyadic form; the square-plate MoM convergence; Hallén vs Galerkin MPIE; reduced-kernel breakdown; the Sommerfeld identity by quadrature; and the grounded-slab TM0 pole and TE1 onset. Output is in `tools/verify/e11_greens_output.txt`.
- `python3 tools/verify/s5_aperture_equivalence.py` (≈ 3 s; W5-S5): loop ↔ magnetic dipole duality; Love equivalence on a sphere (outside reproduced to 10⁻¹⁵, inside extinguished); TE10 aperture patterns, directivity, beamwidths and the variational admittance; reciprocity (free space, PEC image, mixed J/M, gyrator); Bethe hole; Booker. Its §6 grades the openEMS runs and **reports 3 FAILs** (the pre-registered tolerances for the 90 and 150 mm flanges), kept visible on purpose.
- `~/opt/openEMS/venv/bin/python tools/verify/s5_aperture_openems.py F90 F150 F90fine F240` (≈ 3 min in total): flanged WR-90 in openEMS; results in `s5_aperture_openems_results.txt`. (Three "closed NF2FF box" runs in that file returned NaN because the box was set up wrongly; they are ignored.)
- `python3 tools/verify/ant_mom_wire.py` and `ant_mom_general.py` are the Galerkin MPIE wire MoM (08 domain). `tools/verify/sim_nec_vs_mom.py` compares PyNEC with that MoM.
- For layered media: openEMS (FDTD) of a microstrip discontinuity gives the same physics without Green's functions. See `tools/verify/e11_discontinuities_openems.py` and [openEMS workflow](../16-simulation-tools/openems-workflow.md).

## Open questions / gaps
- No layered-media (Sommerfeld-integral) MoM was implemented. The check stops at the identity and the surface-wave pole. A DCIM-based microstrip MoM would be a good future verification of 2.5-D solvers.
- The square-plate extrapolation (0.367) is 1.7 % above the often-quoted ≈ 0.3607, which was not re-checked against a primary source. An edge-refined mesh would settle it.
- Volume integral equations (dielectric bodies, e.g. a fibreglass nose cone in MoM) and the PMCHWT surface formulation for dielectrics are only named here.
- Time-domain integral equations and the periodic (Floquet) Green's function for arrays (D4 noted the latter for 12-phased-arrays) are not covered. Floquet/Bloch analysis of periodic *lines and surfaces* is in [periodic structures and EBG](../03-transmission-lines-matching/periodic-structures-ebg.md).
- The aperture admittance is single-mode variational. Literature values for the flanged WR-90 (e.g. multimode or measured) were not fetched to cross-check the −12.1 dB; openEMS gives −10.7 (λ/20) and −11.8 dB (λ/30), still converging. A closed NF2FF box (with a back face) for the openEMS flange runs remains to be set up.

- A worked loop-star or Calderón example (EFIE low-frequency breakdown) would help anyone writing their own surface MoM at UHF on small structures.

## Sources
1. R. F. Harrington, *Field Computation by Moment Methods*, Macmillan 1968 (IEEE Press reprint 1993), ch. 1 (method, point matching vs Galerkin; charged-plate example), ch. 4 (wire objects). (textbook)
2. W. C. Gibson, *The Method of Moments in Electromagnetics*, 2nd ed., CRC Press 2014, chs. 2–3 (Green's functions, EFIE/MFIE/CFIE, thin-wire kernels), ch. 5 (RWG surfaces), ch. 9 (MLFMM). (textbook)
3. W. C. Chew, *Waves and Fields in Inhomogeneous Media*, IEEE Press 1995, ch. 1 (dyadic Green's function), ch. 2 (layered media, Sommerfeld integrals, branch points and poles). (textbook)
4. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley 2012, ch. 6 (auxiliary potentials), ch. 7 (equivalence, reciprocity), ch. 12 (integral equations; Pocklington, Hallén; MoM); and *Antenna Theory*, 4th ed., ch. 8. (textbook)
5. K. A. Michalski, J. R. Mosig, "Multilayered media Green's functions in integral equation formulations," *IEEE Trans. Antennas Propag.*, 45(3):508–519, 1997. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
6. J. C. Rautio, R. F. Harrington, "An electromagnetic time-harmonic analysis of shielded microstrip circuits," *IEEE Trans. MTT*, 35(8):726–730, 1987 (basis of Sonnet). (peer-reviewed)
7. C.-O. Hwang, M. Mascagni, "Electrical capacitance of the unit cube," *J. Electrostatics* (2004) — reports a preliminary square-plate value C/(4πε0 l) = 0.36 ± 0.01 (seen via search abstract). (peer-reviewed)
8. Y. L. Chow, J. J. Yang, D. G. Fang, G. E. Howard, "A closed-form spatial Green's function for the thick microstrip substrate," *IEEE Trans. MTT*, 39(3):588–592, 1991 (DCIM). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
9. G. J. Burke, A. J. Poggio, *Numerical Electromagnetics Code (NEC) — Method of Moments*, LLNL 1981 (thin-wire and extended kernels, Sommerfeld–Norton ground). (technical report; cited from knowledge)
10. Verification scripts: `tools/verify/e11_greens.py`, `tools/verify/ant_mom_wire.py`; Level 3b: `tools/verify/s5_aperture_equivalence.py`, `tools/verify/s5_aperture_openems.py`. (numerical check)
11. R. F. Harrington, *Time-Harmonic Electromagnetic Fields*, McGraw-Hill 1961 (IEEE Press reissue 2001), ch. 3 (§3-2 duality, §3-3 uniqueness, §3-5 equivalence principle, §3-8 reciprocity, §3-9 reaction), ch. 7 (apertures and the variational aperture admittance). (textbook; cited from knowledge, results re-derived and checked numerically here)
12. C. A. Balanis, *Advanced Engineering Electromagnetics*, 2nd ed., Wiley 2012, ch. 6 (vector potentials A and F), ch. 7 (§7.7 equivalence principle and its forms, §7.8 induction and physical equivalents, §7.9 reciprocity and reaction). (textbook)
13. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley 2016, ch. 12 (aperture antennas: radiation equations with N and L, uniform and TE10 apertures on a ground plane, directivity table; Babinet's principle). (textbook)
14. R. E. Collin, *Field Theory of Guided Waves*, 2nd ed., IEEE Press 1991, ch. 1 (reciprocity, equivalence), ch. 7 (small-aperture coupling, Bethe polarisabilities). (textbook; cited from knowledge)
15. V. H. Rumsey, "Reaction concept in electromagnetic theory," *Phys. Rev.* 94(6):1483–1491, 1954. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
16. H. A. Bethe, "Theory of diffraction by small holes," *Phys. Rev.* 66(7–8):163–182, 1944; and J. D. Jackson, *Classical Electrodynamics*, 3rd ed., §10.9 (transmission cross-section $64k^4a^6/27\pi$). (peer-reviewed / textbook; formula re-derived in the script)
17. H. G. Booker, "Slot aerials and their relation to complementary wire aerials (Babinet's principle)," *J. IEE* 93(IIIA):620–626, 1946. (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
