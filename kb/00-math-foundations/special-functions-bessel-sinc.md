---
title: Special functions in RF — sinc, Bessel, jinc, Fresnel, erf, Chebyshev, Legendre
domain: 00-math-foundations
slug: special-functions-bessel-sinc
tags: [sinc, bessel, jinc, airy, fresnel-integrals, knife-edge, erf, q-function, chebyshev, dolph-chebyshev, legendre, spherical-bessel, modified-bessel, fm-sidebands]
prerequisites: [fourier-series-and-transform.md, differential-equations-circuits-waves.md]
related:
  - probability-random-processes-and-psd.md
  - vector-calculus-for-em.md
  - ../10-comms-modulation/analog-modulation-am-fm-pm-ssb.md
  - ../09-propagation-link-budget/diffraction-knife-edge.md
  - ../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md
  - ../08-antennas/horn-reflector-aperture-antennas.md
  - ../12-phased-arrays/tapering-sidelobe-control.md
  - ../01-circuit-theory/passive-filter-design-prototypes.md
  - ../02-electromagnetics/waveguides-and-cavity-resonators.md
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Special functions in RF — sinc, Bessel, jinc, Fresnel, erf, Chebyshev, Legendre

## Questions this page answers
- What is a sinc function and why does it keep appearing (pulses, apertures, FFT bins)?
- Why does an FM signal have sidebands with Bessel-function amplitudes, and what is Carson's rule?
- How can I calibrate FM deviation with a spectrum analyser (the "Bessel null" method)?
- Why is a dish antenna's beam described by a "jinc"/Airy pattern with −17.6 dB sidelobes?
- What are Fresnel integrals and how do they give knife-edge diffraction loss (6 dB at grazing)?
- What is the Q-function/erfc and where does it appear?
- Why do Chebyshev polynomials appear in both filters and antenna arrays?
- What are Legendre functions and spherical Bessel functions used for?
- Where does the modified Bessel function $I_0$ show up (Rician fading, Kaiser windows)?

## TL;DR
| Function | Definition (short) | Where in RF | Key numbers |
|---|---|---|---|
| sinc | $\mathrm{sinc}(x)=\sin(\pi x)/(\pi x)$ | spectrum of a rect pulse; uniform line aperture pattern; DFT bin response | nulls at integers; sidelobe −13.26 dB; −3 dB at ±0.443 |
| $J_n(\beta)$ | Bessel, 1st kind | FM/PM sideband amplitudes; circular waveguide/patch modes; circular apertures | $J_0$ zero 2.405; $J_1$ zero 3.832; $\sum J_n^2=1$ |
| jinc | $2J_1(u)/u$ | circular aperture (dish, lens) far field | null $\sin\theta=1.22\lambda/D$; HPBW $1.03\lambda/D$; sidelobe −17.6 dB |
| Fresnel $C,S$ | $\int_0^\nu\cos(\pi s^2/2)ds$, $\int_0^\nu\sin(\pi s^2/2)ds$ | knife-edge diffraction; near-field of apertures; chirp spectra | $C,S\to\tfrac12$; knife-edge loss 6.02 dB at ν = 0 |
| erf / erfc / Q | Gaussian integrals | BER, false-alarm probability, Gaussian filter step response | Q(3) = 1.35×10⁻³, Q(4.75) = 10⁻⁶ |
| Chebyshev $T_n$ | $\cos(n\arccos x)$ / $\cosh(n\,\mathrm{arccosh}\,x)$ | equiripple (Chebyshev) filters; Dolph–Chebyshev arrays | 5th-order 0.5 dB-ripple: 42 dB at 2ω_c |
| Legendre $P_n$, $P_n^m$ | solutions in θ of Laplace/Helmholtz | multipole/antenna pattern expansions; spherical near-field | $\int P_mP_n=\frac{2}{2n+1}\delta_{mn}$ |
| spherical Bessel $j_n,h_n$ | radial solutions in spherical coords | radiation, scattering (Mie), near/far field | $h_0^{(2)}(x)=je^{-jx}/x$ (outgoing) |
| modified Bessel $I_0$ | $J_0$ of imaginary argument | Rician PDF; Kaiser window; Marcum Q | $I_0(0)=1$ |

All values verified in `tools/verify/math_special_functions.py`.

## Intuition (no math)
"Special functions" are just the named solutions of equations that keep recurring. Sines and cosines are the solutions for straight, box-shaped problems. Bessel functions are the "sines and cosines of circles": the natural vibration shapes of a drumhead, the field patterns in a round waveguide, the pattern of a round dish. Legendre functions play the same role for spheres. Fresnel integrals describe what happens when a wave only partly passes an edge — the gradual transition from light to shadow behind a hill. The error function is "how much of a bell curve lies beyond a point" — the probability that noise exceeds a threshold. Chebyshev polynomials are the functions that wiggle as little as possible within a band and then shoot up as fast as possible outside it — exactly what you want from a filter or from an array's sidelobes.

You rarely need to evaluate them by hand — `scipy.special` does it — but you need to recognise them, know their landmark values, and know what physical question each answers.

## The math

### Level 1 — landmarks you should recognise

- **sinc**: the spectrum of any sharp-edged, flat-topped thing (a pulse, a uniformly lit aperture, a rectangular FFT window). Zero at every nonzero integer; first sidelobe −13.3 dB; sidelobes fall as $1/x$ (−20 dB/decade). See [Fourier](fourier-series-and-transform.md).
- **FM sidebands**: an FM tone of modulation index $\beta=\Delta f/f_m$ has lines at $f_c\pm nf_m$ with amplitudes $J_n(\beta)$. Small β: only $J_0\approx1$, $J_{\pm1}\approx\beta/2$ (narrowband FM looks like AM with a phase twist). Large β: bandwidth ≈ $2(\Delta f+f_m)$ (Carson's rule).
- **Dish beamwidth**: HPBW ≈ $1.03\lambda/D$ radians for uniform illumination (≈ 59°·λ/D); real dishes with edge taper are ≈ $1.2\lambda/D$ (≈ 70°·λ/D).
- **Knife-edge**: a hill that just touches the line of sight costs 6 dB; clearing it by 0.6 of the first Fresnel zone costs ~0 dB.
- **Gaussian tails**: Q(x) is the chance noise exceeds x standard deviations.

### Level 2 — definitions, identities, and derivations

**Bessel functions of the first kind** $J_n(x)$ solve Bessel's equation $x^2y''+xy'+(x^2-n^2)y=0$, which is what the radial part of the Helmholtz equation becomes in cylindrical coordinates ([ODEs/PDEs](differential-equations-circuits-waves.md)). A generating identity ties them to phase modulation — the **Jacobi–Anger expansion** [1 §10.12]:
$$e^{j\beta\sin\theta}=\sum_{n=-\infty}^{\infty}J_n(\beta)e^{jn\theta}.$$
Put $\theta=2\pi f_mt$: an FM/PM signal $\cos(2\pi f_ct+\beta\sin2\pi f_mt)=\mathrm{Re}\{e^{j2\pi f_ct}e^{j\beta\sin2\pi f_mt}\}$ has spectral lines at $f_c+nf_m$ with amplitudes $J_n(\beta)$ [2]. Properties: $J_{-n}=(-1)^nJ_n$; $\sum_nJ_n^2(\beta)=1$ (power is conserved — FM is constant-envelope); $J_0(2.405)=0$ (carrier vanishes); $J_1(3.832)=0$. Verified by FFT of a synthetic FM signal (line amplitudes equal $|J_n(2)|$ to $10^{-12}$).
- **Carson's rule**: $B\approx2(\beta+1)f_m=2(\Delta f+f_m)$ contains ≥98 % of the power (verified: 99.9 % at β = 1, 99.4 % at β = 5) [2].
- **Bessel-null method**: set $f_m$, raise deviation until the carrier line disappears on a spectrum analyser: then $\beta=2.405$ and $\Delta f=2.405f_m$. Next carrier nulls at β = 5.520, 8.654.

Other Bessel family members:
- $Y_n$ (second kind, singular at 0) — needed for coax (annular) regions.
- $H_n^{(1,2)}=J_n\pm jY_n$ (Hankel) — outgoing/incoming cylindrical waves; with $e^{j\omega t}$, $H^{(2)}$ is outgoing.
- Modified $I_n(x)=j^{-n}J_n(jx)$, $K_n$ — evanescent/decaying fields; $I_0$ appears in the Rician PDF ([probability](probability-random-processes-and-psd.md)) and the Kaiser window $w[n]=I_0(\pi\alpha\sqrt{1-(2n/N-1)^2})/I_0(\pi\alpha)$.
- Zeros $j_{mn}$ (of $J_m$) and $j'_{mn}$ (of $J'_m$) set circular waveguide cutoffs: TE₁₁ uses $j'_{11}=1.841$: $f_c=1.841c/(2\pi a)$; they also set circular patch resonances.

**Jinc and the circular aperture.** The 2-D Fourier transform of a uniformly illuminated circular aperture of diameter $D$ is
$$E(\theta)\propto\frac{2J_1(u)}{u},\qquad u=\frac{\pi D}{\lambda}\sin\theta$$
(since $\int_0^{2\pi}e^{jx\cos\phi}d\phi=2\pi J_0(x)$ and $\int_0^ax J_0(kx)dx=aJ_1(ka)/k$). Landmarks (verified): first null at $u=3.832$ ⇒ $\sin\theta=1.2197\lambda/D$ (the "Rayleigh criterion"); half power at $u=1.616$ ⇒ HPBW $=1.029\lambda/D$; first sidelobe −17.57 dB. Tapered illumination (edge taper 10–15 dB) widens the beam to ~$1.2\lambda/D$ and drops sidelobes to ~−25 dB. See [aperture antennas](../08-antennas/horn-reflector-aperture-antennas.md).

**Fresnel integrals** [1 §7.2], [3 §2.7]:
$$C(\nu)=\int_0^\nu\cos\frac{\pi s^2}{2}ds,\qquad S(\nu)=\int_0^\nu\sin\frac{\pi s^2}{2}ds,\qquad C,S\to\tfrac12\ \text{as}\ \nu\to\infty.$$
The curve $(C(\nu),S(\nu))$ is the Cornu spiral. They arise whenever a quadratic phase ($e^{j\pi s^2/2}$) is integrated over a finite range: diffraction past an edge (path length differences grow quadratically with transverse offset), near-field (Fresnel-region) behaviour of apertures, and the band-edge ripples of a chirp's spectrum ([Fourier](fourier-series-and-transform.md)).

**Knife-edge diffraction** (ITU-R P.526-14 §4.1) [3]. With obstacle height $h$ above the direct line (negative if below), distances $d_1,d_2$ from the ends:
$$\nu=h\sqrt{\frac{2}{\lambda}\left(\frac1{d_1}+\frac1{d_2}\right)}=\sqrt2\,\frac{h}{r_1},\qquad r_1=\sqrt{\frac{\lambda d_1d_2}{d_1+d_2}}\ (\text{first Fresnel zone radius}),$$
$$J(\nu)=-20\log_{10}\frac{\sqrt{(1-C(\nu)-S(\nu))^2+(C(\nu)-S(\nu))^2}}{2}\ \text{dB}\qquad(\text{eq. 30}),$$
approximated for $\nu>-0.78$ by $J(\nu)\approx6.9+20\log_{10}\left(\sqrt{(\nu-0.1)^2+1}+\nu-0.1\right)$ (eq. 31). Verified: exact $J(0)=6.02$ dB; approximation within 0.13 dB of exact for ν from −0.5 to 5. Details and multiple edges: [knife-edge diffraction](../09-propagation-link-budget/diffraction-knife-edge.md).

**Error function family** [1 §7.2]: $\mathrm{erf}(z)=\frac{2}{\sqrt\pi}\int_0^ze^{-t^2}dt$, $\mathrm{erfc}=1-\mathrm{erf}$, $Q(x)=\tfrac12\mathrm{erfc}(x/\sqrt2)$. Uses: BER and false-alarm probabilities ([probability](probability-random-processes-and-psd.md)); the step response of a Gaussian filter is an erf (Gaussian-filtered FSK — GFSK — edges; scope rise-time models).

**Chebyshev polynomials** [1 §18.3]: $T_0=1$, $T_1=x$, $T_{n+1}=2xT_n-T_{n-1}$; $T_n(x)=\cos(n\arccos x)$ for $|x|\le1$ (oscillates between ±1 with equal ripples) and $\cosh(n\,\mathrm{arccosh}\,x)$ for $|x|>1$ (grows as fast as any polynomial of degree n can: $\approx2^{n-1}x^n$). Verified for n = 3, 5, 8.
- **Chebyshev type-I filter**: $|H(j\omega)|^2=\dfrac{1}{1+\varepsilon^2T_n^2(\omega/\omega_c)}$, ripple $r$ dB ⇒ $\varepsilon=\sqrt{10^{r/10}-1}$ (0.5 dB → 0.349). 5th-order, 0.5 dB ripple: 42.0 dB attenuation at $2\omega_c$ versus 30.1 dB for a 5th-order Butterworth (verified against `scipy.signal.cheby1`). Price: passband ripple and worse group delay ([filter prototypes](../01-circuit-theory/passive-filter-design-prototypes.md)).
- **Dolph–Chebyshev array** [4]: for an $N$-element broadside array with spacing $d$, the array factor is a polynomial of degree $N-1$ in $\cos(\psi/2)$, $\psi=kd\cos\theta$. Matching it to $T_{N-1}(x_0\cos(\psi/2))$ with $x_0=\cosh\left(\frac{1}{N-1}\mathrm{arccosh}R\right)$, $R$ = main-lobe/sidelobe voltage ratio, gives **all sidelobes equal** at $1/R$ and the narrowest main beam possible for that sidelobe level. Verified: 8 elements, λ/2 spacing, 30 dB ($R=31.62$, $x_0=1.1807$) → weights ≈ [0.262, 0.519, 0.812, 1, 1, 0.812, 0.519, 0.262], every sidelobe at −30.0 dB, HPBW 16.4° vs 12.8° uniform (whose first sidelobe is −12.8 dB for N = 8). `scipy.signal.windows.chebwin` computes these weights (same maths as a Dolph–Chebyshev window in spectral analysis). See [tapering](../12-phased-arrays/tapering-sidelobe-control.md).

### Level 3 — spherical problems and asymptotics

**Legendre functions.** Separating Laplace's or Helmholtz's equation in spherical coordinates, the θ-equation is Legendre's equation; regular solutions on the whole sphere are $P_n(\cos\theta)$ (axisymmetric) and associated $P_n^m(\cos\theta)$, combining with $e^{jm\phi}$ into spherical harmonics $Y_n^m$ [1 §14, §18.3]. Orthogonality $\int_{-1}^1P_mP_n\,dx=\frac{2}{2n+1}\delta_{mn}$ (verified) lets any pattern be expanded in multipoles: $n=1$ is the dipole ($\sin\theta$ pattern), $n=2$ the quadrupole, etc. Uses: spherical-wave expansions for near-field antenna measurement, the Chu limit on small-antenna Q (the lowest-order spherical mode sets a minimum stored energy — see [small antenna limits](../08-antennas/small-antenna-limits.md)), and Mie scattering from spheres (radar calibration spheres).

**Spherical Bessel and Hankel functions.** The radial equation gives $j_n(kr)$, $y_n(kr)$ and $h_n^{(2)}(kr)=j_n-jy_n$. Elementary forms: $j_0(x)=\sin x/x$, $h_0^{(2)}(x)=je^{-jx}/x$ — the outgoing spherical wave $e^{-jkr}/r$ in the $e^{j\omega t}$ convention (verified). Higher orders contain the $1/(jkr)^2$, $1/(jkr)^3$ near-field terms that appear in the Hertzian-dipole fields ([vector calculus](vector-calculus-for-em.md)).

**Asymptotic forms** (useful for back-of-envelope work and numerical sanity checks) [1 §10.17, §10.40]:
- $J_n(x)\approx\sqrt{\frac{2}{\pi x}}\cos\left(x-\frac{n\pi}{2}-\frac\pi4\right)$ for $x\gg n$ — Bessel functions look like decaying cosines, zeros spaced ≈ π.
- $J_n(x)\approx\frac{(x/2)^n}{n!}$ for $x\ll1$ — narrowband FM sidebands $\approx\beta/2$.
- $I_0(x)\approx e^x/\sqrt{2\pi x}$ for large x (verified at x = 50) — why the Rician PDF becomes Gaussian at high K.
- $\mathrm{erfc}(z)\approx\frac{e^{-z^2}}{z\sqrt\pi}$ for large z.
- Fresnel: $C(\nu)\approx\tfrac12+\frac{\sin(\pi\nu^2/2)}{\pi\nu}$, $S(\nu)\approx\tfrac12-\frac{\cos(\pi\nu^2/2)}{\pi\nu}$ for large ν — hence knife-edge loss ≈ $20\log_{10}(\pi\nu\sqrt2)$ ≈ $13+20\log_{10}\nu$ dB deep in shadow.

**Other functions you will meet.** Elliptic functions (Cauer/elliptic filters, conformal maps for CPW/stripline impedance formulas); the gamma function (chi-square/gamma distributions; $\Gamma(1/2)=\sqrt\pi$); Marcum Q (radar detection with a steady target); exponential integral (ground-wave and some antenna mutual-impedance formulas); Airy functions (caustics, turning points in ionospheric propagation).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| lines at $f_c\pm nf_m$, amplitude $J_n(\beta)$ | sinusoidal FM/PM | β = 5: carrier $J_0^2=-15$ dBc |
| $B_{\rm Carson}=2(\Delta f+f_m)$ | FM, ≥98 % power | Δf = 5 kHz, f_m = 1 kHz → 12 kHz |
| carrier null at β = 2.405, 5.520, 8.654 | FM deviation calibration | |
| HPBW $\approx1.03\lambda/D$ (uniform), $\approx1.2\lambda/D$ (tapered) | circular aperture, $D\gg\lambda$ | 1 m dish @ 5.8 GHz: 3.0° |
| first null $\sin\theta=1.22\lambda/D$ | uniform circular aperture | |
| $\nu=\sqrt2h/r_1$; $J(0)=6$ dB | single knife edge | $h=0.6r_1$ below LOS ⇒ ~0 dB |
| $J(\nu)\approx6.9+20\log(\sqrt{(\nu-0.1)^2+1}+\nu-0.1)$ | $\nu>-0.78$ (ITU-R P.526) | ν = 1 → 13.9 dB |
| $\varepsilon=\sqrt{10^{r/10}-1}$ | Chebyshev ripple r dB | 0.5 dB → 0.349 |
| $x_0=\cosh(\mathrm{arccosh}(R)/(N-1))$ | Dolph–Chebyshev | N = 8, 30 dB: 1.181 |

## Worked examples

**1. Calibrating an FM (or FSK) deviation.** Modulate a 433.92 MHz test transmitter with a 1.000 kHz tone and increase deviation until the carrier line vanishes on a spectrum analyser (RBW ≪ 1 kHz): deviation = 2.405 kHz. For a 5 kHz deviation with 1 kHz tone (β = 5) the carrier is at −15 dBc and Carson's bandwidth is 12 kHz. (For digital 2-FSK/GFSK the spectrum is not a simple Bessel comb; see [digital modulation](../10-comms-modulation/digital-modulation-psk-qam-fsk.md).)

**2. Narrowband phase modulation from phase noise or vibration.** A reference oscillator vibrating on a rocket gets a small sinusoidal phase modulation with peak β = 0.2 rad at 100 Hz: sidebands at ±100 Hz with $J_1(0.2)/J_0(0.2)=0.0995/0.990$ → −20.0 dBc each — the vibration-induced spurs seen on crystal oscillators during flight ([phase noise](../07-noise-linearity/phase-noise-and-jitter.md)).

**3. Ground-station dish.** A 1 m dish at 5.8 GHz (λ = 51.7 mm): uniform-illumination HPBW 3.05°, first null 3.6°; with realistic taper, ≈3.5° HPBW. Tracking a rocket at 10 km with a 3.5° beam requires pointing to ±~1° to keep loss under ~1 dB (the loss of a Gaussian-ish beam at offset θ is ≈ $12(\theta/\mathrm{HPBW})^2$ dB). At 433 MHz a 1 m "dish" would be only 1.4λ across — use a Yagi instead ([ground-station tracking Yagi](../20-projects-recipes/ground-station-tracking-yagi.md)).

**4. Hill between rocket recovery site and ground station.** 10 km path at 433 MHz, hill at the midpoint rising 20 m above the line of sight: $r_1=\sqrt{0.692\times5000\times5000/10000}=41.6$ m, $\nu=\sqrt2\times20/41.6=0.68$, $J=11.6$ dB extra loss (verified). Raising the ground antenna so the line clears the hilltop by $0.6r_1=25$ m brings the loss to ≈ 0 dB ([Fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)).

**5. Low-sidelobe 8-element array.** For a 2.4 GHz 8-patch linear array (λ/2 spacing) needing −30 dB sidelobes to reject interference, use Dolph–Chebyshev weights [0.26, 0.52, 0.81, 1, 1, 0.81, 0.52, 0.26] (amplitude); beamwidth grows from 12.8° to 16.4°, and the taper efficiency loss is $10\log_{10}\left[(\sum w)^2/(N\sum w^2)\right]=-0.75$ dB for these weights (verified) ([array factor](../12-phased-arrays/array-factor-linear-arrays.md)).

**6. Chebyshev vs Butterworth harmonic filter.** A 5th-order low-pass after a 433 MHz PA with cutoff 500 MHz must attenuate the 866 MHz 2nd harmonic ($\omega/\omega_c=1.73$). Butterworth: $10\log(1+1.73^{10})=23.8$ dB; Chebyshev 0.5 dB ripple: $10\log(1+0.349^2T_5^2(1.73))=34.6$ dB (both verified). The Chebyshev buys ~11 dB at the cost of 0.5 dB passband ripple and worse group delay (see [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md)).

## Practical notes
- `scipy.special`: `jv, yv, jn_zeros, jnp_zeros, i0, iv, kv, hankel2, spherical_jn, spherical_yn, fresnel` (returns **(S, C)** in that order), `erf, erfc, erfcinv, eval_chebyt, eval_legendre, lpmv, gamma`. `scipy.stats.norm.sf` = Q.
- Check conventions: some texts define Fresnel integrals with argument $s^2$ instead of $\pi s^2/2$; ITU-R and scipy use $\pi s^2/2$.
- Numerical traps: `jv` of large order and small argument underflows (fine); `i0` overflows above ~700 (use `i0e`, the scaled version); Chebyshev $T_n$ for $|x|>1$ grows enormous — work in dB.

## Common mistakes & misconceptions
1. **Unnormalised vs normalised sinc** — `numpy.sinc(x)=sin(πx)/(πx)`; many texts use $\sin x/x$. Nulls move from integers to multiples of π.
2. **"FM bandwidth = 2Δf."** Carson adds $2f_m$; for small β the bandwidth is ≈ $2f_m$ regardless of Δf.
3. **Assuming FM sideband powers add up to more than the carrier power** — total power is constant ($\sum J_n^2=1$); modulation just redistributes it.
4. **Using the 1-D sinc sidelobe (−13.3 dB) for a dish** — circular apertures give −17.6 dB (uniform) and lower with taper.
5. **Treating knife-edge loss as zero whenever the direct line is clear** — loss starts when the obstacle enters ~0.6 of the first Fresnel zone; at grazing it is 6 dB.
6. **Swapping (S, C)** from `scipy.special.fresnel`.
7. **Thinking Dolph–Chebyshev is "best" in all respects** — it minimises beamwidth for a given equal-sidelobe level, but far sidelobes don't decay (bad for wideband interference and grating-lobe-adjacent energy); Taylor distributions are often preferred for large arrays.
8. **Forgetting the Hankel-function convention** — with $e^{j\omega t}$, outgoing waves are $H^{(2)}$/$h^{(2)}$; physics texts ($e^{-i\omega t}$) use $H^{(1)}$.

## How to simulate / verify
- `python3 tools/verify/math_special_functions.py` — sinc integral; FM Bessel identities and FFT of synthetic FM; Carson power fraction; jinc landmarks; Fresnel limits; ITU-R P.526 knife-edge exact vs approximate and J(0) = 6.02 dB; Fresnel-zone example; Chebyshev polynomial forms; Chebyshev filter vs `cheby1`; Dolph–Chebyshev 8-element 30 dB array with equal sidelobes; Legendre orthogonality; spherical Hankel outgoing wave; I₀ asymptote; Γ(½). All PASS.

## Open questions / gaps
- Taylor n̄ distributions and Bayliss difference patterns (monopulse) belong to 12-phased-arrays; only named here.
- Worked example 6 compares ideal prototype responses only; 06-rf-circuits should give an exact doubly-terminated design (element values, component Q) for Marcus's 433 MHz PA.

## Sources
1. NIST *Digital Library of Mathematical Functions* (F. W. J. Olver et al., eds.), https://dlmf.nist.gov : ch. 7 (error functions and Fresnel integrals, §7.2 definitions), ch. 10 (Bessel functions: §10.2 definitions, §10.12 generating function/Jacobi–Anger, §10.17 asymptotics, §10.25 modified, §10.40 asymptotics of modified, §10.47 spherical Bessel), ch. 14 (Legendre functions), ch. 18 (orthogonal polynomials, §18.3 Chebyshev and Legendre) (standard reference).
2. H. Taub, D. L. Schilling, *Principles of Communication Systems*, 2nd ed., McGraw-Hill (1986), ch. 4 (FM: Bessel-function spectrum, Carson's rule) — or equivalently S. Haykin, *Communication Systems*, 4th ed., Wiley (2001), §2.7 (textbooks; NOT verified — W5-S18, 2026-10-13, found no 2nd-ed. Taub & Schilling ToC and no section-level Haykin 4th-ed. ToC; later Taub & Schilling editions title ch. 4 "Angle Modulation", consistent with the citation).
3. ITU-R Recommendation P.526-14 (01/2018), *Propagation by diffraction*: §2.7 Fresnel integrals (eqs. 6–7), §4.1 single knife-edge obstacle (eqs. 26–31). https://www.itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.526-14-201801-I!!PDF-E.pdf (standard; read via pdftotext).
4. C. L. Dolph, "A current distribution for broadside arrays which optimizes the relationship between beam width and side-lobe level," *Proc. IRE* 34(6):335–348 (1946). https://ieeexplore.ieee.org/document/1697083/ (peer-reviewed).
5. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley (2016): ch. 6 (arrays, §6.8 non-uniform amplitude: binomial and Dolph–Tschebyscheff), ch. 12 (aperture antennas, §12.3–12.7 radiation equations, rectangular and circular apertures) (textbook; checked by W5-S18 against the Wiley 4th-ed. ToC in gaps/D4-curriculum.md §3.2).
6. SciPy documentation, `scipy.special` and `scipy.signal.windows.chebwin`. https://docs.scipy.org/doc/scipy/reference/special.html (software documentation).
