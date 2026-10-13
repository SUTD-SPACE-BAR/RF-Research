---
title: Vector calculus for electromagnetics
domain: 00-math-foundations
slug: vector-calculus-for-em
tags: [vector-calculus, gradient, divergence, curl, laplacian, gauss-theorem, stokes-theorem, spherical-coordinates, cylindrical-coordinates, phasor-fields, helmholtz-equation]
prerequisites: [complex-numbers-and-phasors.md, differential-equations-circuits-waves.md]
related:
  - ../02-electromagnetics/maxwells-equations.md
  - ../02-electromagnetics/wave-equation-plane-waves-polarization.md
  - ../02-electromagnetics/poynting-vector-power-flow.md
  - ../02-electromagnetics/boundary-conditions-reflection-refraction.md
  - ../02-electromagnetics/radiation-from-currents-hertzian-dipole.md
  - ../02-electromagnetics/inductance-capacitance-from-fields.md
  - ../08-antennas/antenna-fundamentals.md
  - special-functions-bessel-sinc.md
  - numerical-methods-overview.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Vector calculus for electromagnetics

## Questions this page answers
- What do gradient, divergence, curl and the Laplacian mean physically?
- How do I read Maxwell's equations in words?
- What do the divergence (Gauss) theorem and Stokes' theorem let me do in practice?
- Why do antenna books use spherical coordinates, and why do the formulas look so messy there?
- Why can't I take the Laplacian of each component of a vector in spherical coordinates?
- What is a "phasor vector field", and why does $\nabla\times\mathbf E=-j\omega\mu\mathbf H$ have a $j$ in it?
- Where does $e^{-jkr}/r$ come from, and what is the Helmholtz equation?
- How far from an antenna does the near field stop mattering?

## TL;DR
- **Gradient** $\nabla f$: points uphill, magnitude = steepest slope. $\mathbf E=-\nabla V$ in electrostatics.
- **Divergence** $\nabla\cdot\mathbf F$: net outflow per unit volume ("sourciness"). Gauss: $\nabla\cdot\mathbf D=\rho$ — charge is where $\mathbf D$ lines start.
- **Curl** $\nabla\times\mathbf F$: circulation per unit area, axis by right-hand rule ("swirliness"). Faraday: $\nabla\times\mathbf E=-\partial\mathbf B/\partial t$; Ampère–Maxwell: $\nabla\times\mathbf H=\mathbf J+\partial\mathbf D/\partial t$.
- **Laplacian** $\nabla^2f$: how much $f$ differs from the average of its neighbourhood. Wave/Helmholtz equations are built from it.
- **Divergence theorem**: $\oint\mathbf F\cdot d\mathbf S=\int\nabla\cdot\mathbf F\,dV$. **Stokes**: $\oint\mathbf F\cdot d\boldsymbol\ell=\int(\nabla\times\mathbf F)\cdot d\mathbf S$. They convert between the integral (lab-measurable: flux, EMF, current) and differential (local) forms of Maxwell, and give boundary conditions.
- Identities: $\nabla\times\nabla f=0$, $\nabla\cdot\nabla\times\mathbf F=0$, $\nabla\times\nabla\times\mathbf F=\nabla(\nabla\cdot\mathbf F)-\nabla^2\mathbf F$ (the last with $\nabla^2\mathbf F$ taken component-wise **only in Cartesian**).
- Phasor fields: $\mathbf E(\mathbf r,t)=\mathrm{Re}\{\mathbf E(\mathbf r)e^{j\omega t}\}$ so $\partial/\partial t\to j\omega$. For a plane wave $e^{-j\mathbf k\cdot\mathbf r}$, $\nabla\to-j\mathbf k$: Maxwell's equations become algebra.
- $e^{-jkr}/r$ is the outgoing spherical wave solving $\nabla^2\psi+k^2\psi=0$; near-field terms of a small antenna fall as $1/(kr)^2,1/(kr)^3$ and equal the radiating term at $r=\lambda/2\pi$ (11.0 cm at 433 MHz).

## Intuition (no math)
A vector field is a map with an arrow at every point: wind on a weather map, water flow in a river, the electric field around a charged PCB trace. Three questions you can ask of such a map:
1. **Where is the uphill?** (for a scalar map like height or voltage) — the gradient. Electric field points *downhill* in voltage, towards lower potential.
2. **Is stuff being created or destroyed here?** Draw a tiny box; count arrows going out minus arrows coming in. A tap in a bath is a positive source, a plughole a negative one. That is divergence. Electric field lines start on positive charge and end on negative charge; magnetic field lines never start or end — there are no magnetic "taps" ($\nabla\cdot\mathbf B=0$).
3. **Does it swirl?** Drop a tiny paddle wheel in the flow. If it spins, the field has curl. The magnetic field wraps around a current like water around a plughole vortex. A *changing* magnetic field creates a swirling electric field — that swirl, pushed around a loop of wire, is the voltage induced in a loop antenna or transformer.

Caution: "curl" is about local rotation, not about lines being curved. A river flowing straight but faster in the middle than at the banks has curl (the paddle wheel spins); a vortex whose speed falls as $1/r$ has *no* curl except at its centre. The field around a wire is the second kind.

Maxwell's equations in words: electric field lines start and end on charges; magnetic lines form closed loops; a changing magnetic field makes the electric field swirl; currents and a changing electric field make the magnetic field swirl. The last two feed each other — a changing E makes a swirling H, whose change makes a swirling E, and so on: an electromagnetic wave.

The two big theorems say "what happens inside a region shows up on its boundary": total sourciness inside a box = total flux out through its walls; total swirliness over a surface = circulation around its edge. That is why you can measure current by the magnetic field around a wire (current probe) or voltage by the flux through a loop.

## The math

### Level 1 — vectors, fields and integrals

Vectors $\mathbf A=A_x\hat{\mathbf x}+A_y\hat{\mathbf y}+A_z\hat{\mathbf z}$.
- Dot product $\mathbf A\cdot\mathbf B=|A||B|\cos\theta$ (projection; work; power flow through a surface).
- Cross product $\mathbf A\times\mathbf B$: magnitude $|A||B|\sin\theta$, direction by right-hand rule (torque, Lorentz force $q\mathbf v\times\mathbf B$, Poynting vector $\mathbf E\times\mathbf H$).

Integrals of fields:
- **Line integral** $\int_C\mathbf F\cdot d\boldsymbol\ell$: e.g. voltage $V_{ab}=-\int_a^b\mathbf E\cdot d\boldsymbol\ell$; EMF around a loop.
- **Flux** $\int_S\mathbf F\cdot d\mathbf S$: e.g. current $I=\int\mathbf J\cdot d\mathbf S$; magnetic flux $\Phi=\int\mathbf B\cdot d\mathbf S$; power through a surface $\int\mathbf S_{\rm Poynting}\cdot d\mathbf S$.
- **Volume integral** $\int_V\rho\,dV$: total charge, stored energy.

Maxwell's equations in integral form (SI; $\mathbf D=\varepsilon\mathbf E$, $\mathbf B=\mu\mathbf H$ in simple media):

| Law | Integral form | Meaning |
|---|---|---|
| Gauss (E) | $\oint_S\mathbf D\cdot d\mathbf S=Q_{\rm enc}$ | flux of D out of a closed surface = enclosed charge |
| Gauss (B) | $\oint_S\mathbf B\cdot d\mathbf S=0$ | no magnetic charge |
| Faraday | $\oint_C\mathbf E\cdot d\boldsymbol\ell=-\frac{d}{dt}\int_S\mathbf B\cdot d\mathbf S$ | EMF = −rate of change of flux |
| Ampère–Maxwell | $\oint_C\mathbf H\cdot d\boldsymbol\ell=I_{\rm enc}+\frac{d}{dt}\int_S\mathbf D\cdot d\mathbf S$ | circulation of H = conduction + displacement current |

Full treatment: [Maxwell's equations](../02-electromagnetics/maxwells-equations.md).

### Level 2 — the operators, the theorems, and curvilinear coordinates

**Cartesian definitions** [1 §1.2]:
$$\nabla f=\frac{\partial f}{\partial x}\hat{\mathbf x}+\frac{\partial f}{\partial y}\hat{\mathbf y}+\frac{\partial f}{\partial z}\hat{\mathbf z},\qquad \nabla\cdot\mathbf F=\frac{\partial F_x}{\partial x}+\frac{\partial F_y}{\partial y}+\frac{\partial F_z}{\partial z},$$
$$\nabla\times\mathbf F=\begin{vmatrix}\hat{\mathbf x}&\hat{\mathbf y}&\hat{\mathbf z}\\ \partial_x&\partial_y&\partial_z\\ F_x&F_y&F_z\end{vmatrix},\qquad \nabla^2f=\nabla\cdot\nabla f=\partial_x^2f+\partial_y^2f+\partial_z^2f.$$

**Coordinate-free definitions** (these are what the operators *mean*):
$$\nabla\cdot\mathbf F=\lim_{\Delta V\to0}\frac{1}{\Delta V}\oint_{\partial V}\mathbf F\cdot d\mathbf S,\qquad \hat{\mathbf n}\cdot(\nabla\times\mathbf F)=\lim_{\Delta S\to0}\frac{1}{\Delta S}\oint_{\partial S}\mathbf F\cdot d\boldsymbol\ell.$$
Summing these over many tiny cells, interior contributions cancel and only the boundary survives — which *is* the proof of the two big theorems:

**Fundamental theorems** [1 §1.3.3–1.3.5], [2 §6.7–6.8]:
- Gradient theorem: $\int_a^b\nabla f\cdot d\boldsymbol\ell=f(b)-f(a)$ (path-independent ⇒ conservative field, curl-free).
- Divergence (Gauss) theorem: $\int_V\nabla\cdot\mathbf F\,dV=\oint_{\partial V}\mathbf F\cdot d\mathbf S$.
- Stokes' theorem: $\int_S(\nabla\times\mathbf F)\cdot d\mathbf S=\oint_{\partial S}\mathbf F\cdot d\boldsymbol\ell$.
(Both checked numerically in `tools/verify/math_vector_calculus.py` on a cube and a disk.) Applying them to the integral Maxwell equations for an arbitrarily small volume/loop gives the **differential form**:
$$\nabla\cdot\mathbf D=\rho,\quad\nabla\cdot\mathbf B=0,\quad\nabla\times\mathbf E=-\frac{\partial\mathbf B}{\partial t},\quad\nabla\times\mathbf H=\mathbf J+\frac{\partial\mathbf D}{\partial t}.$$
Taking the divergence of the last and using $\nabla\cdot\nabla\times=0$ gives charge conservation $\nabla\cdot\mathbf J=-\partial\rho/\partial t$ — displacement current is *required* for consistency.

**Identities** (verified symbolically) [1 §1.2.6–1.2.7]:
- $\nabla\times(\nabla f)=0$ — gradients have no curl (static E is conservative).
- $\nabla\cdot(\nabla\times\mathbf A)=0$ — curls have no divergence (so $\mathbf B=\nabla\times\mathbf A$ automatically satisfies $\nabla\cdot\mathbf B=0$).
- $\nabla\times\nabla\times\mathbf F=\nabla(\nabla\cdot\mathbf F)-\nabla^2\mathbf F$.
- Product rules: $\nabla\cdot(f\mathbf F)=f\nabla\cdot\mathbf F+\mathbf F\cdot\nabla f$; $\nabla\cdot(\mathbf E\times\mathbf H)=\mathbf H\cdot\nabla\times\mathbf E-\mathbf E\cdot\nabla\times\mathbf H$ (the origin of Poynting's theorem, [Poynting](../02-electromagnetics/poynting-vector-power-flow.md)).

**Helmholtz decomposition.** A field that decays suitably at infinity is fixed by its divergence and curl: $\mathbf F=-\nabla\Phi+\nabla\times\mathbf A$ [1 §1.6]. That is why Maxwell's four equations (two divergences, two curls) are enough, and why potentials $V,\mathbf A$ exist.

**Cylindrical coordinates** $(\rho,\phi,z)$ — wires, coax, monopoles [1 §1.4.2]:
$$d\mathbf l=d\rho\,\hat{\boldsymbol\rho}+\rho\,d\phi\,\hat{\boldsymbol\phi}+dz\,\hat{\mathbf z},\quad dV=\rho\,d\rho\,d\phi\,dz$$
$$\nabla f=\partial_\rho f\,\hat{\boldsymbol\rho}+\frac1\rho\partial_\phi f\,\hat{\boldsymbol\phi}+\partial_zf\,\hat{\mathbf z},\qquad \nabla\cdot\mathbf F=\frac1\rho\partial_\rho(\rho F_\rho)+\frac1\rho\partial_\phi F_\phi+\partial_zF_z$$
$$\nabla\times\mathbf F=\left(\frac1\rho\partial_\phi F_z-\partial_zF_\phi\right)\hat{\boldsymbol\rho}+(\partial_zF_\rho-\partial_\rho F_z)\hat{\boldsymbol\phi}+\frac1\rho\left(\partial_\rho(\rho F_\phi)-\partial_\phi F_\rho\right)\hat{\mathbf z}$$
$$\nabla^2f=\frac1\rho\partial_\rho(\rho\,\partial_\rho f)+\frac1{\rho^2}\partial_\phi^2f+\partial_z^2f$$

**Spherical coordinates** $(r,\theta,\phi)$, $\theta$ from the $+z$ axis — antennas, radiation, scattering [1 §1.4.1]:
$$d\mathbf l=dr\,\hat{\mathbf r}+r\,d\theta\,\hat{\boldsymbol\theta}+r\sin\theta\,d\phi\,\hat{\boldsymbol\phi},\quad dV=r^2\sin\theta\,dr\,d\theta\,d\phi,\quad d\Omega=\sin\theta\,d\theta\,d\phi$$
$$\nabla f=\partial_rf\,\hat{\mathbf r}+\frac1r\partial_\theta f\,\hat{\boldsymbol\theta}+\frac{1}{r\sin\theta}\partial_\phi f\,\hat{\boldsymbol\phi}$$
$$\nabla\cdot\mathbf F=\frac{1}{r^2}\partial_r(r^2F_r)+\frac{1}{r\sin\theta}\partial_\theta(\sin\theta\,F_\theta)+\frac{1}{r\sin\theta}\partial_\phi F_\phi$$
$$\nabla\times\mathbf F=\frac{1}{r\sin\theta}\left[\partial_\theta(\sin\theta F_\phi)-\partial_\phi F_\theta\right]\hat{\mathbf r}+\frac1r\left[\frac{1}{\sin\theta}\partial_\phi F_r-\partial_r(rF_\phi)\right]\hat{\boldsymbol\theta}+\frac1r\left[\partial_r(rF_\theta)-\partial_\theta F_r\right]\hat{\boldsymbol\phi}$$
$$\nabla^2f=\frac1{r^2}\partial_r(r^2\partial_rf)+\frac{1}{r^2\sin\theta}\partial_\theta(\sin\theta\,\partial_\theta f)+\frac{1}{r^2\sin^2\theta}\partial_\phi^2f$$
Why the extra factors: the unit vectors $\hat{\mathbf r},\hat{\boldsymbol\theta},\hat{\boldsymbol\phi}$ change direction from point to point, and the lengths of coordinate steps ($r\,d\theta$, $r\sin\theta\,d\phi$) depend on position. The operators must account for both. Antennas use spherical coordinates because radiated fields depend on $r$ only through $e^{-jkr}/r$ and all the angular structure (the pattern) separates into $(\theta,\phi)$. Solid angle: a full sphere is $4\pi$ sr, which is where the $4\pi$ in isotropic gain and in $A_e=G\lambda^2/4\pi$ comes from.

**Conversions**: $x=r\sin\theta\cos\phi$, $y=r\sin\theta\sin\phi$, $z=r\cos\theta$; $\hat{\mathbf z}=\cos\theta\,\hat{\mathbf r}-\sin\theta\,\hat{\boldsymbol\theta}$ (used to express a $z$-directed current in spherical components).

### Level 3 — phasor vector fields, Helmholtz equation, radiation, delta functions

**Phasor (time-harmonic) fields.** With $\mathbf E(\mathbf r,t)=\mathrm{Re}\{\mathbf E(\mathbf r)e^{j\omega t}\}$ — a *complex vector* at every point (each Cartesian component has its own amplitude and phase; that is what describes elliptical/circular polarisation) — Maxwell becomes
$$\nabla\times\mathbf E=-j\omega\mu\mathbf H,\qquad \nabla\times\mathbf H=\mathbf J+j\omega\varepsilon\mathbf E,\qquad\nabla\cdot\mathbf D=\rho,\qquad\nabla\cdot\mathbf B=0.$$
Losses enter through complex $\varepsilon=\varepsilon'-j\varepsilon''$ (and $\sigma$: $j\omega\varepsilon\to j\omega\varepsilon+\sigma$). Time-averaged power density: $\langle\mathbf S\rangle=\tfrac12\mathrm{Re}\{\mathbf E\times\mathbf H^*\}$ (peak phasors) [3 §1.6].

**Plane waves: $\nabla\to-j\mathbf k$.** For fields $\propto e^{-j\mathbf k\cdot\mathbf r}$, each derivative just multiplies by $-jk_x$ etc., so $\nabla\times\mathbf E=-j\mathbf k\times\mathbf E$ and the curl equations give $\mathbf H=\frac{1}{\eta}\hat{\mathbf k}\times\mathbf E$, $\eta=\sqrt{\mu/\varepsilon}$ (376.7 Ω in vacuum), $\mathbf E\perp\mathbf H\perp\mathbf k$. Verified symbolically for $\mathbf E=\hat{\mathbf x}E_0e^{-jkz}$ [4]. See [plane waves](../02-electromagnetics/wave-equation-plane-waves-polarization.md).

**Vector Helmholtz equation.** In a source-free, homogeneous region, take the curl of Faraday and use the identity: $\nabla\times\nabla\times\mathbf E=\nabla(\nabla\cdot\mathbf E)-\nabla^2\mathbf E=-\nabla^2\mathbf E$, so
$$\nabla^2\mathbf E+k^2\mathbf E=0,\qquad k=\omega\sqrt{\mu\varepsilon}=\frac{2\pi}{\lambda}.$$
Caution: $\nabla^2\mathbf E$ means "Laplacian of each Cartesian component". In curvilinear coordinates use $\nabla(\nabla\cdot\mathbf E)-\nabla\times\nabla\times\mathbf E$ instead, because $\hat{\mathbf r},\hat{\boldsymbol\theta}$ themselves vary. Solutions by separation of variables give sinusoids (Cartesian), Bessel functions (cylindrical: waveguides, circular apertures) and spherical Bessel/Legendre functions (spherical: radiation, scattering) — see [differential equations](differential-equations-circuits-waves.md), [special functions](special-functions-bessel-sinc.md).

**Green's function and the $e^{-jkr}/r$ wave.** $\psi=e^{-jkr}/r$ satisfies $\nabla^2\psi+k^2\psi=0$ for $r\ne0$ (verified), and more precisely $(\nabla^2+k^2)\frac{e^{-jkr}}{4\pi r}=-\delta^3(\mathbf r)$. With the magnetic vector potential ($\mathbf B=\nabla\times\mathbf A$, Lorenz gauge), $\nabla^2\mathbf A+k^2\mathbf A=-\mu\mathbf J$, so
$$\mathbf A(\mathbf r)=\frac{\mu}{4\pi}\int\mathbf J(\mathbf r')\frac{e^{-jk|\mathbf r-\mathbf r'|}}{|\mathbf r-\mathbf r'|}dV'.$$
This one integral is the basis of antenna theory and of method-of-moments solvers (NEC) ([numerical methods](numerical-methods-overview.md)).

**Hertzian dipole in three lines.** A short current element $Il\,\hat{\mathbf z}$ at the origin: $\mathbf A=\hat{\mathbf z}\frac{\mu Il}{4\pi r}e^{-jkr}$ with $\hat{\mathbf z}=\cos\theta\hat{\mathbf r}-\sin\theta\hat{\boldsymbol\theta}$. Applying the spherical curl, $\mathbf H=\frac1\mu\nabla\times\mathbf A$ has only a $\phi$ component:
$$H_\phi=\frac{jkIl\sin\theta}{4\pi r}\left(1+\frac{1}{jkr}\right)e^{-jkr}$$
(verified symbolically with sympy). Then $\mathbf E=\frac{1}{j\omega\varepsilon}\nabla\times\mathbf H$ gives $E_\theta$ with $1,\ 1/(jkr),\ 1/(jkr)^2$ terms and $E_r$ with $1/(jkr)$, $1/(jkr)^2$ terms. The $1/r$ terms carry radiated power; the others are reactive near fields. They are equal in magnitude at $kr=1$, $r=\lambda/2\pi$. Full development: [Hertzian dipole](../02-electromagnetics/radiation-from-currents-hertzian-dipole.md), [near/far field](../02-electromagnetics/near-field-far-field.md).

**Delta functions in 3-D.** $\nabla\cdot(\hat{\mathbf r}/r^2)=4\pi\delta^3(\mathbf r)$ and $\nabla^2(1/r)=-4\pi\delta^3(\mathbf r)$ [1 §1.5]: zero everywhere except the origin (verified), but with total flux $4\pi$ (verified) — a point charge.

**Boundary conditions from the theorems.** A flat "pillbox" (divergence theorem) across an interface gives $\hat{\mathbf n}\cdot(\mathbf D_1-\mathbf D_2)=\rho_s$, $\hat{\mathbf n}\cdot(\mathbf B_1-\mathbf B_2)=0$; a thin rectangular loop (Stokes) gives $\hat{\mathbf n}\times(\mathbf E_1-\mathbf E_2)=0$, $\hat{\mathbf n}\times(\mathbf H_1-\mathbf H_2)=\mathbf J_s$. On a perfect conductor, tangential E = 0 and the surface current equals the tangential H jump — the basis of ground planes and image theory ([boundary conditions](../02-electromagnetics/boundary-conditions-reflection-refraction.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $H=I/(2\pi\rho)$ | long straight wire (Ampère) | 1 A at 1 cm: 15.9 A/m |
| $E=\dfrac{V}{\rho\ln(b/a)}$ | coax, $a<\rho<b$ (Gauss) | max at inner conductor |
| $C'=\dfrac{2\pi\varepsilon}{\ln(b/a)}$, $L'=\dfrac{\mu}{2\pi}\ln\dfrac ba$ | coax (TEM) | RG-58-like: 97 pF/m, 259 nH/m, 51.7 Ω |
| $\mathrm{EMF}=-j\omega\mu_0H_nA$ | small loop, uniform field | 1 cm², 1 A/m, 433 MHz: 0.34 V |
| $\mathbf H=\hat{\mathbf k}\times\mathbf E/\eta$ | plane wave | 1 V/m ↔ 2.65 mA/m ↔ 1.33 mW/m² |
| $\langle S\rangle=\tfrac12\mathrm{Re}\{\mathbf E\times\mathbf H^*\}$ | peak phasors | |
| $k=2\pi/\lambda$; near/far crossover $r=\lambda/2\pi$ | small antenna | 433 MHz: $k=9.08$ rad/m, 11.0 cm |
| $\oint\mathbf D\cdot d\mathbf S=Q$; $\oint\mathbf H\cdot d\boldsymbol\ell=I$ | always (with displacement current) | |

## Worked examples

**1. Magnetic field near a current-carrying trace/wire.** A 1 A supply current in a long wire: $\oint\mathbf H\cdot d\boldsymbol\ell=I$ around a circle of radius $\rho$ gives $H\cdot2\pi\rho=I$ ⇒ $H=15.9$ A/m at 1 cm ($B=\mu_0H=20$ µT — half of Earth's field, which is about 40 µT in Singapore; this is why a flight-computer magnetometer is so sensitive to nearby battery, servo and regulator currents, and why the Space Bar practice is to calibrate hard/soft iron on the assembled airframe). Check: the field is curl-free off the wire and its circulation is exactly $I$ (verified).

**2. Coax from Gauss's law.** Charge $q'$ per metre on the inner conductor (radius $a$), return on the outer (radius $b$). A cylindrical Gaussian surface of radius $\rho$: $D\cdot2\pi\rho=q'$ ⇒ $E=q'/(2\pi\varepsilon\rho)$. Integrate for voltage: $V=\frac{q'}{2\pi\varepsilon}\ln(b/a)$ ⇒ $C'=2\pi\varepsilon/\ln(b/a)$. Ampère gives $L'=\frac{\mu}{2\pi}\ln(b/a)$, and $Z_0=\sqrt{L'/C'}=\frac{60}{\sqrt{\varepsilon_r}}\ln\frac ba$. With $a=0.405$ mm, $b=1.475$ mm, $\varepsilon_r=2.25$ (RG-58-like): $C'=96.8$ pF/m, $L'=258.5$ nH/m, $Z_0=51.7$ Ω. Peak field at the inner conductor with 2 W (14.1 V peak) is $14.1/(0.405\,\text{mm}\times\ln3.64)=27$ kV/m — far below air breakdown (~3 MV/m), so 2 W is no problem. See [coax](../03-transmission-lines-matching/coax-and-cables.md), [inductance and capacitance from fields](../02-electromagnetics/inductance-capacitance-from-fields.md).

**3. Plane wave at 433 MHz.** $k=2\pi f/c=9.075$ rad/m ($\lambda=69.2$ cm). $\mathbf E=\hat{\mathbf x}\,1\,\text{V/m}\,e^{-jkz}$ ⇒ $\mathbf H=\hat{\mathbf y}\,2.65\,\text{mA/m}\,e^{-jkz}$; $\langle S\rangle=\frac{|E|^2}{2\eta}=1.33$ mW/m² (peak-phasor convention; with 1 V/m *rms* it would be 2.65 mW/m²).

**4. Small H-field probe / loop antenna (Stokes + Faraday).** A 1 cm² loop in a uniform 1 A/m, 433 MHz field normal to it: $\mathrm{EMF}=\omega\mu_0HA=2\pi(433\times10^6)(4\pi\times10^{-7})(1)(10^{-4})=0.34$ V. This is how near-field EMC probes work ([EMC](../13-pcb-rf-layout-emc/emc-emi-fundamentals.md), [loop antennas](../08-antennas/loop-antennas.md)).

**5. Near-field distance around a rocket antenna.** At 433 MHz, the reactive terms of a small dipole match the radiating term at $r=\lambda/2\pi=11.0$ cm and fall off rapidly beyond. Avionics, batteries and metal structure within ~10–20 cm of a 433 MHz antenna couple strongly to its near field (detuning, pattern distortion); at 915 MHz the same boundary is 5.2 cm. See [antennas on rockets](../08-antennas/antennas-on-rockets.md).

## Practical notes
- **Symbolic help**: `sympy.vector.CoordSys3D` with `transformation='spherical'` or `'cylindrical'` gives correct grad/div/curl including scale factors (used in the verify script).
- **Right-hand rule sanity check**: current up the $+z$ axis ⇒ $\mathbf H$ circulates in $+\hat{\boldsymbol\phi}$ (counter-clockwise viewed from above).
- **Units**: E in V/m, D in C/m², H in A/m, B in T (= Wb/m²), J in A/m², ρ in C/m³.
- **Numerical EM** discretises exactly these operators: FDTD uses the curl equations on a staggered grid; FEM uses the curl–curl equation weakly; MoM uses the Green's-function integral ([numerical methods](numerical-methods-overview.md)).

## Common mistakes & misconceptions
1. **"Curved field lines = curl, straight lines = no curl."** Curl is local rotation; shear in a straight flow has curl, while the $1/\rho$ field around a wire is curl-free off the wire [5].
2. **Using Cartesian component Laplacians in spherical/cylindrical coordinates** — unit vectors vary; use the $\nabla\nabla\cdot-\nabla\times\nabla\times$ form.
3. **Forgetting scale factors** ($\rho$, $r$, $r\sin\theta$) in line/area/volume elements — e.g. writing $dV=dr\,d\theta\,d\phi$ loses $r^2\sin\theta$ and gives wrong radiated power.
4. **Confusing θ and φ conventions** — physics/antenna convention: θ = polar angle from $+z$, φ = azimuth. Some maths texts swap them.
5. **Dropping displacement current** — without $j\omega\mathbf D$ there are no waves and no radiation, and charge conservation fails.
6. **Peak vs rms phasors in the Poynting vector** — ½ factor (3 dB) errors, as for circuit power ([phasors](complex-numbers-and-phasors.md)).
7. **Sign of $j$** — physics texts use $e^{-i\omega t}$: $\nabla\times\mathbf E=i\omega\mathbf B$ and outgoing waves $e^{+ikr}$.
8. **Thinking $\nabla\cdot\mathbf E=0$ always** — only where there is no free charge; at conductor surfaces, trace edges and dielectric interfaces charge accumulates.

## How to simulate / verify
- `python3 tools/verify/math_vector_calculus.py` — sympy: curl grad = 0, div curl = 0, curl curl identity; spherical Laplacian of 1/r; $e^{-jkr}/r$ solves Helmholtz; wire field curl-free with circulation I; Gauss flux 4π; plane-wave H from curl E; **Hertzian dipole $H_\phi$ from curl A in spherical coordinates**; numeric divergence theorem (cube) and Stokes theorem (disk). All PASS.
- Visualise fields with `matplotlib.pyplot.streamplot`/`quiver`; compute numerical div/curl with `numpy.gradient` on a grid.

## Open questions / gaps
- Dyadic Green's functions and vector spherical harmonics (for full multipole expansions and spherical near-field antenna measurement) are not covered; add if 08-antennas/antenna-measurement needs them.

## Sources
1. D. J. Griffiths, *Introduction to Electrodynamics*, 4th ed., Pearson/Cambridge (2013/2017), ch. 1 "Vector analysis": §1.2 differential calculus (gradient, divergence, curl, product rules, second derivatives), §1.3 integral calculus (fundamental theorems for gradients, divergences, curls), §1.4 curvilinear coordinates (spherical 1.4.1, cylindrical 1.4.2), §1.5 Dirac delta, §1.6 theory of vector fields (Helmholtz theorem, potentials) (textbook).
2. OpenStax, *Calculus Volume 3* (2016), §6.5 "Divergence and curl", §6.7 "Stokes' theorem", §6.8 "The divergence theorem". https://openstax.org/books/calculus-volume-3/pages/6-5-divergence-and-curl (textbook, free).
3. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley (2012), §1.2 Maxwell's equations in phasor form, §1.6 energy and power (textbook; section numbers checked by W5-S18 (2026-10-13) against the Wiley 4th-ed. ToC transcribed in gaps/D4-curriculum.md §3.1).
4. F. T. Ulaby, U. Ravaioli, *Fundamentals of Applied Electromagnetics*, 7th ed., Pearson (2015), ch. 3 "Vector analysis" (coordinate systems, gradient/divergence/curl/Laplacian), ch. 6–7 (Maxwell's equations, plane waves) (textbook).
5. Physics Forums, "Intuition on divergence and curl" (2016). https://www.physicsforums.com/threads/intuition-on-divergence-and-curl.881895/ (forum — anecdotal; used for the misconception list).
6. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, Rutgers (online ed.), ch. 1 (Maxwell's equations) and ch. 15 (radiation from linear antennas, vector potential) (textbook, free) — chapter numbers confirmed against the 2016 edition's table of contents (ch. 15 "Radiation Fields", §15.2 retarded potentials) by W5-S18, 2026-10-13.
