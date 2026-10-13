---
title: Waveguides and cavity resonators (rectangular, circular, parallel-plate, SIW, PCB plane cavities; transverse resonance, modal V/I, probe and loop excitation)
domain: 02-electromagnetics
slug: waveguides-and-cavity-resonators
tags: [waveguide, TE, TM, TEM, cutoff, dispersion, phase-velocity, group-velocity, wave-impedance, attenuation, cavity, Q-factor, SIW, below-cutoff, plane-resonance, circular-waveguide, TE11, TE01, TM01, TM010, TE011, parallel-plate, transverse-resonance, slab-loaded-guide, surface-wave, modal-voltage-current, probe-feed, loop-coupling, bethe-hole, cantenna]
prerequisites: [wave-equation-plane-waves-polarization.md, boundary-conditions-reflection-refraction.md, skin-effect-conductor-loss-roughness.md]
related: [quasi-static-vs-full-wave.md, poynting-vector-power-flow.md, ../03-transmission-lines-matching/coax-and-cables.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, ../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md, ../08-antennas/horn-reflector-aperture-antennas.md, ../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md, ../13-pcb-rf-layout-emc/shielding-and-isolation.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Waveguides and cavity resonators (rectangular, circular, SIW, PCB plane cavities)

## Questions this page answers
- How does a hollow metal pipe carry microwaves, and why does it have a cutoff frequency?
- What are TE, TM and TEM modes, and why can't a hollow waveguide carry TEM?
- What waveguide size would I need at 433 MHz, 915 MHz, 2.45 GHz or 10 GHz?
- Phase velocity is faster than light in a waveguide — doesn't that break relativity?
- How lossy is a waveguide compared with coax?
- How do cavity resonators work, and what limits their Q?
- Why does a small hole or a honeycomb vent block RF (waveguide beyond cutoff)?
- What is a substrate-integrated waveguide (SIW)?
- Why does my PCB's power/ground plane pair resonate at a few hundred MHz?
- Why does a circular waveguide (a can) have such a narrow single-mode band, and what does its TE11 mode look like?
- What is the transverse-resonance method, and how does it find surface waves on a PCB?
- What is "the impedance" of a waveguide when there are several definitions?
- How long should the probe in a cantenna be, and where should it go?
- How do probes, loops and small holes couple energy into a waveguide?

## TL;DR
- A hollow conductor supports only **TE (H) and TM (E) modes**, each with a **cutoff frequency f_c**; below f_c the mode decays exponentially. **TEM needs two separate conductors** (coax, microstrip, stripline) and has no cutoff [1][2].
- **Rectangular guide (a × b, a > b)**: f_c,mn = (c/2√εr)√((m/a)² + (n/b)²). Dominant **TE10: f_c = c/(2a)**. WR-90 (22.86 × 10.16 mm): f_c = 6.557 GHz, used 8.2–12.4 GHz. For 2.45 GHz: WR-430 (109 × 55 mm, f_c 1.37 GHz); 915 MHz: WR-975 (248 × 124 mm); 433 MHz: WR-2300 (584 × 292 mm!). Verified in `tools/verify/em_waveguides.py`.
- **Dispersion**: β = √(k² − k_c²); **λ_g = λ0/√(1 − (f_c/f)²)**; **v_p = c/√(1−(f_c/f)²) > c**, **v_g = c√(1−(f_c/f)²) < c**, v_p·v_g = c². Energy and information travel at v_g.
- **Wave impedance**: Z_TE = η/√(1−(f_c/f)²) (> η), Z_TM = η√(1−(f_c/f)²) (< η).
- **Loss**: copper WR-90 TE10 ≈ **0.11 dB/m at 10 GHz**; WR-430 at 2.45 GHz ≈ 0.009 dB/m — far lower than coax of practical size.
- **Below cutoff**: attenuation ≈ **27.3 dB per width** (rectangular TE10) or **32 dB per diameter** of length (circular TE11) for f ≪ f_c: a 5 mm hole 10 mm deep attenuates 2.45 GHz by ≈ 64 dB.
- **Cavity resonators**: a closed box resonates at discrete frequencies; rectangular TE101 f0 = (c/2)√(1/a² + 1/d²). Copper air cavities reach **Q_c ≈ 8 000 (X-band WR-90 section) to 15 000 (2.45 GHz, 87 × 40 × 87 mm)**; total 1/Q = 1/Q_c + 1/Q_d + 1/Q_ext, with Q_d = 1/tanδ.
- **PCB plane pairs are cavities**: a 100 × 50 mm FR-4 board resonates at **715 MHz**, 1.43, 1.60 GHz… with Q ≈ 30 (h = 0.2 mm) — right in the UHF bands.
- **SIW**: two rows of plated vias in a laminate act as waveguide walls; a_eff ≈ w − d²/(0.95s) (Cassivi/Deslandes & Wu) [5][6].
- **Circular guide (Level 3b):** single-mode band only **1.31 : 1** (TE11 → TM01); TE11 carries two polarisations; TE01 loss falls with frequency. **Transverse resonance** turns layered cross-sections into 1-D circuits (TM0 on JLC 1.43 mm FR-4: β/k0 = 1.00165 at 2.45 GHz). **Modal V/I**: WR-90 "impedance" is 274–499 Ω depending on the definition; only ratios are physical.
- **Excitation:** probe resistance $2Z_{TE}d^2\sin^2\beta l/(ab)$ from mode orthogonality; WR-90 probe 50 Ω at ≈ 0.58b; 90 mm cantenna at 2.45 GHz: short **λg/4 = 50.6 mm** behind a radial probe of **≈ 31 mm** (50 Ω resistance).

## Intuition (no math)
Think of a TE10 wave in a rectangular guide as two plane waves bouncing back and forth between the
side walls at an angle, zig-zagging down the guide. Their interference pattern has zero E-field at the
walls (as a conductor requires) and a maximum in the middle. The zig-zag angle depends on frequency:
at high frequency the waves travel nearly straight down the guide; as frequency falls they bounce more
steeply, until at the cutoff frequency they bounce straight across (half a wavelength fits exactly
between the side walls) and make no progress at all. Below cutoff the wave can't fit and the field just
decays.

Because the wave zig-zags, the crests of the interference pattern sweep along the guide faster than
light (like the point where an ocean wave meets a sea wall), while the energy — carried along each
zig-zag path — progresses more slowly than light. No information moves faster than c.

A cavity is a waveguide closed at both ends: waves bounce back and forth and only fit at discrete
frequencies. With nothing but slightly lossy copper walls, energy survives for thousands of cycles —
Q in the thousands to tens of thousands, far beyond any lumped LC.

## The math

### Level 1 — mode formulas

Rectangular guide, inner width a (x), height b (y), filled with εr, μr = 1; guide axis z; e^{jωt − jβz}.

| Quantity | Formula | Units |
|---|---|---|
| cutoff wavenumber | k_c,mn = √((mπ/a)² + (nπ/b)²) | rad/m |
| cutoff frequency | f_c,mn = k_c/(2π√(με)) = (c/2√εr)√((m/a)²+(n/b)²) | Hz |
| propagation constant | β = √(k² − k_c²) (real above cutoff); α = √(k_c² − k²) below | rad/m, Np/m |
| guide wavelength | λ_g = 2π/β = λ/√(1 − (f_c/f)²) | m |
| phase / group velocity | v_p = ω/β; v_g = dω/dβ = v²/v_p | m/s |
| TE wave impedance | Z_TE = E_t/H_t = kη/β | Ω |
| TM wave impedance | Z_TM = βη/k | Ω |

TE_mn exists for m, n ≥ 0 (not both 0); TM_mn needs m, n ≥ 1. With a = 2b (standard WR guides) the
order is TE10, then TE20 = TE01, then TE11/TM11; single-mode bandwidth is f_c10 to 2f_c10, used
≈ 1.25–1.9 f_c (script: WR-90 → 8.2–12.5 GHz).

Circular guide of radius R: f_c = c·p/(2πR√εr) with p a Bessel-function zero: **TE11 p = 1.8412**
(dominant), **TM01 2.4048**, TE21 3.0542, **TE01 3.8317** (= TM11, degenerate). TE01's attenuation
*falls* with frequency — historically proposed for long-haul millimetre-wave trunks.

**Waveguide sizes for Marcus's bands** (TE10, script):

| Guide | a × b (mm) | f_c TE10 | Recommended band |
|---|---|---|---|
| WR-2300 | 584 × 292 | 257 MHz | 0.32–0.49 GHz (433 MHz fits) |
| WR-975 | 248 × 124 | 605 MHz | 0.76–1.15 GHz (915 MHz fits) |
| WR-650 | 165 × 83 | 908 MHz | 1.14–1.73 GHz (GNSS L1 fits) |
| WR-430 | 109 × 55 | 1.372 GHz | 1.72–2.61 GHz (2.45 GHz ISM, microwave ovens) |
| WR-90 | 22.9 × 10.2 | 6.557 GHz | 8.2–12.4 GHz (X-band) |

At UHF waveguides are absurdly large — that is why coax and planar lines rule below ~2 GHz, and why
waveguide becomes attractive in the mm-wave radar bands (24/77 GHz, WR-42/WR-12).

### Level 2 — derivation (TE modes of a rectangular guide)

For fields ∝ e^{−jβz}, Maxwell's curl equations let every transverse field component be written in
terms of the axial components E_z and H_z (Pozar §3.1 [1]). For TE modes (E_z = 0), H_z satisfies the
2-D Helmholtz equation
$$\left(\frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2} + k_c^2\right)h_z = 0,\qquad k_c^2 = k^2 - \beta^2.$$
Separation of variables gives h_z = A cos(mπx/a) cos(nπy/b), where the boundary condition E_tan = 0 on
the walls (⇔ ∂h_z/∂n = 0) fixes k_x = mπ/a, k_y = nπ/b. For TE10:
$$E_y = -\frac{j\omega\mu a}{\pi}A\sin\frac{\pi x}{a}e^{-j\beta z},\quad H_x = \frac{j\beta a}{\pi}A\sin\frac{\pi x}{a}e^{-j\beta z},\quad H_z = A\cos\frac{\pi x}{a}e^{-j\beta z}.$$
Why no TEM in a hollow guide: TEM requires k_c = 0, so the transverse field is a solution of Laplace's
equation — a static field — which inside a single closed conductor must be zero (the conductor is an
equipotential). Two conductors (coax) allow a non-zero static-like transverse field → TEM.

Group velocity from β: dβ/dω = k/(βv) ⇒ v_g = v·β/k = v√(1 − (f_c/f)²); v_p·v_g = v². WR-90 at 10 GHz:
λ_g = 39.7 mm (vs λ0 = 30.0 mm), v_p = 1.32c, v_g = 0.755c, Z_TE = 499 Ω (script; numerical dω/dβ
agrees).

### Level 2 — attenuation

**Conductor loss** by the perturbation method (Poynting flux into the walls = ½R_s|H_tan|²; see
[skin effect](skin-effect-conductor-loss-roughness.md)): for TE10,
$$\alpha_c = \frac{R_s}{a^3b\beta k\eta}\left(2b\pi^2 + a^3k^2\right)\ \text{Np/m}\quad(\text{Pozar eq. 3.96 [1]}).$$
Script (copper, smooth; numerical wall-loss integral agrees to 10⁻⁶): **WR-90: 0.148 dB/m at 8 GHz,
0.108 at 10 GHz, 0.098 at 12 GHz; WR-430 at 2.45 GHz: 0.0086 dB/m.** α_c rises steeply near cutoff
(v_g → 0, fields bounce many times per metre) and has a broad minimum in the band. Real guides are
~10–30 % lossier (roughness, plating, joints).

**Dielectric loss** of a filled guide: α_d = k²tanδ/(2β) — larger than in TEM by the factor k/β.

**Below cutoff** (f < f_c): γ = α = √(k_c² − k²) ≈ k_c for f ≪ f_c. Rectangular TE10 k_c = π/a →
8.686π = **27.3 dB per length a**; circular TE11 k_c = 1.8412/R → **32.0 dB per diameter**. The field
decays but carries no real power (reactive, evanescent). Uses: waveguide-beyond-cutoff vents and
honeycomb panels in shielded enclosures, cutoff attenuators, and understanding why small apertures
leak little at low frequency — a 5 mm diameter hole 10 mm deep (f_c 35 GHz) attenuates 2.45 GHz by
64 dB (script), whereas a *thin* 5 mm hole in a 0.5 mm wall gives only ~3 dB of cutoff attenuation and
leaks by aperture coupling instead (see [shielding](../13-pcb-rf-layout-emc/shielding-and-isolation.md)).

### Level 3 — cavity resonators

Short-circuit a guide at z = 0 and z = d: standing waves fit when βd = ℓπ. Rectangular TE_mnℓ:
$$f_{mn\ell} = \frac{c}{2\sqrt{\varepsilon_r}}\sqrt{\left(\frac ma\right)^2 + \left(\frac nb\right)^2 + \left(\frac \ell d\right)^2}.$$
**Q** = ω·(stored energy)/(power lost). For TE101 in a copper cavity (Pozar eq. 6.46 [1]):
$$Q_c = \frac{(kad)^3b\eta}{2\pi^2R_s}\cdot\frac{1}{2a^3b + 2bd^3 + a^3d + ad^3},\qquad Q_d = \frac{1}{\tan\delta},\qquad \frac{1}{Q_0} = \frac1{Q_c} + \frac1{Q_d}.$$
Script: WR-90 section 22.2 mm long → f0 = 9.41 GHz, Q_c ≈ 7 800; an 86.6 × 40 × 86.6 mm air box →
2.448 GHz, **Q_c ≈ 15 600** (numerical energy/loss integration agrees exactly). Adding a dielectric of
tanδ = 10⁻⁴ caps Q at 10 000 → total 6 100. Loaded Q adds coupling: 1/Q_L = 1/Q_0 + 1/Q_ext. Q_c scales
as (size/δ) — bigger cavities and lower frequencies with larger dimensions have higher Q; silver plating
buys ~3 %, roughness costs more.

Where Marcus meets cavities:
- **Cavity filters** for duplexers/ground stations (coaxial-resonator or combline filters are
  cavity-like; unloaded Q of 1 000–5 000 at UHF gives low-loss, steep filters) —
  [RF filters](../06-rf-circuits/rf-filters-lc-saw-baw-cavity-microstrip.md).
- **Shielding cans and enclosures resonate**: an empty metal box 50 × 40 × 10 mm has its first TE101
  mode at (c/2)√(1/0.05² + 1/0.04²) = 4.8 GHz — above UHF, but a 150 × 100 mm enclosure resonates near
  1.8 GHz and can couple an LO to an antenna port. Absorber sheets lower its Q.
- **PCB power/ground plane pairs** are parallel-plate cavities (open edges ≈ magnetic walls):
  f_mn = (c/2√εr)√((m/A)² + (n/B)²). A 100 × 50 mm FR-4 board: **715 MHz (TM10), 1.43 GHz (TM01, TM20),
  1.60 GHz (TM11)** (script). Their Q: 1/Q = tanδ + δ/h (+ radiation): for h = 0.2 mm, tanδ = 0.02 →
  Q ≈ 31. At resonance the plane-pair impedance peaks — decoupling capacitors (with their mounting
  inductance) or lossy dielectrics damp it. This matters for LoRa and GNSS: plane resonances couple
  digital noise into RF sections ([PDN for RF](../13-pcb-rf-layout-emc/power-distribution-decoupling-for-rf.md)).

### Level 3 — substrate-integrated waveguide (SIW)

Replace the side walls of a dielectric-filled rectangular guide by two rows of plated through-holes
(diameter d, pitch s, row spacing w) in a laminate with copper top and bottom. The TE10-like mode
propagates as in a solid-wall guide of equivalent width
$$a_\text{eff} \approx w - \frac{d^2}{0.95\,s}\quad(\text{Cassivi et al. 2002; Deslandes \& Wu})\ [5][6],$$
provided leakage between vias is small: s ≤ 2d and d ≪ λ_g (commonly d < λ_g/5). Only TE_m0 modes exist
(the vias can't carry the longitudinal wall currents of TE_mn with n ≥ 1, and the thin substrate
suppresses them). Script (RO4003C, εr 3.55): w = 20 mm, d = 1.0 mm, s = 1.8 mm → a_eff = 19.4 mm,
f_c = 4.10 GHz (usable ≈ 5–7.8 GHz: a 5.8 GHz SIW); w = 15 mm → f_c = 5.48 GHz. SIW enables low-loss,
self-shielded filters, couplers, slot arrays and horn feeds on ordinary PCBs at 5.8 GHz and above
(JLCPCB via-drill limits: 13-pcb). Below ~3 GHz SIWs become very wide (∝ 1/(f√εr)).

### Level 3b — circular guides in depth, parallel plates, transverse resonance, modal V/I and excitation

All numbers in this subsection come from `tools/verify/s5_waveguide_extras.py` (W5-S5).

**A. Circular guide (radius R).** TE modes take $h_z=J_n(p'_{nm}\rho/R)\cos n\phi$, TM modes $e_z=J_n(p_{nm}\rho/R)\cos n\phi$, with $k_c=p/R$ (p′ = zero of $J_n'$, p = zero of $J_n$). The order is TE11 (1.8412) < TM01 (2.4048) < TE21 (3.0542) < TE01 = TM11 (3.8317). Three practical facts follow.
- **The single-mode band is only 1.31 : 1** (2.4048/1.8412), against 2 : 1 for a rectangular guide with a = 2b. A 90 mm can has TE11 at 1.952 GHz and TM01 at 2.550 GHz, so 2.45 GHz sits 4 % below the second mode.
- **TE11 is two modes.** The cos φ and sin φ solutions have the same β, so the guide carries any polarisation, including circular. That is what circular feeds and orthomode transducers exploit. It also means a dent or slight ellipticity couples the two and slowly rotates or depolarises the wave.
- **Loss.** Wall-loss integration of the mode fields confirms the closed forms
$$\alpha_c^{TE_{nm}}=\frac{R_s}{Rk\eta\beta}\Big(k_c^2+\frac{n^2k^2}{p'^2_{nm}-n^2}\Big),\qquad\alpha_c^{TM_{nm}}=\frac{R_sk}{R\eta\beta}$$
to 3 × 10⁻⁸. A 90 mm can at 2.45 GHz loses **0.0115 dB/m in copper and 0.029 dB/m in tin** (tinplate, σ = 9.17 × 10⁶ S/m): irrelevant over 0.2 m. TE01 ($n=0$) has $\alpha\propto k_c^2/(k\beta)$, which *falls* with frequency (R = 25 mm: 0.044 → 0.0008 dB/m from 8 to 64 GHz). That is why it was once the candidate for long millimetre-wave trunks; it must be kept from converting to TE11/TM11.

**B. Parallel-plate guide (spacing d, filled with εr).** It supports TEM (no cutoff) plus TE_n and TM_n with $k_c=n\pi/d$, i.e. $f_c=nc/(2d\sqrt{\varepsilon_r})$. For a 0.2 mm FR-4 plane pair the first higher mode is at **357 GHz**, and for a 1.6 mm board at 44.7 GHz. So the PCB plane-pair resonances of Level 3 are *TEM* waves standing between the board edges. The TEM loss is $\alpha_c=R_s/(\eta d)$ plus $\alpha_d=\tfrac12k\tan\delta$: 1.91 + 3.49 dB/m for the 0.2 mm FR-4 pair at 915 MHz, so $Q=\beta/2\alpha$ = 32. That agrees with the $1/Q=\tan\delta+\delta/h$ estimate in Level 3 (31), as it must.

**C. Transverse resonance.** If the cross-section is layered along one transverse direction (say x), each layer is a transmission line *across* the guide with $k_{x,i}=\sqrt{k_i^2-\beta^2}$ and impedance $Z_i=\omega\mu/k_{x,i}$ (fields TE to x) or $k_{x,i}/(\omega\varepsilon_i)$ (TM to x). A mode exists where the impedances looking both ways from any plane sum to zero, $\overrightarrow Z(x_0)+\overleftarrow Z(x_0)=0$. It turns a 2-D field problem into a 1-D circuit problem (Collin [3][9], Marcuvitz [8]).
- *Empty rectangular guide:* two short-circuited lines, $\tan k_xa=0$, so $k_x=m\pi/a$. This is the familiar result.
- *WR-90 with a dielectric slab against one side wall* (thickness t, εr): $k_d\cot(k_dt)+k_a\cot(k_a(a-t))=0$. Against a 1-D finite-difference eigen-solver: t = 5 mm, εr 2.2 at 8 GHz gives β = 108.88 rad/m (FD 108.91); a half-filled guide gives 133.000 rad/m in both. Slab loading is how dielectric phase shifters and partially filled SIW lines are designed.
- *Grounded slab (surface waves):* TM, $k_d\tan(k_dh)=\varepsilon_r\alpha$; TE, $-k_d\cot(k_dh)=\alpha$, with $\alpha=\sqrt{\beta^2-k_0^2}$. On JLC's 1.43 mm core (εr 4.5) the TM0 wave has **β/k0 = 1.000051, 1.000228, 1.00165, 1.00967, 1.0321 and 1.341** at 0.434, 0.915, 2.45, 5.8, 10 and 24 GHz. TE1 starts at 28.0 GHz. The thin-slab asymptote is $\beta/k_0\approx1+\tfrac12[k_0h(1-1/\varepsilon_r)]^2$ (within 0.02 % at 433 MHz). The same routine reproduces the 1.51 mm values in [Green's functions](greens-functions-and-integral-equations.md) and the 1.6 mm values in [planar arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md). What surface waves do to antennas is in [periodic structures and EBG](../03-transmission-lines-matching/periodic-structures-ebg.md).

**D. Modal voltage and current: why "the impedance of a waveguide" is ambiguous.** Write the transverse fields of one mode as $\mathbf E_t=V(z)\,\mathbf e(x,y)$ and $\mathbf H_t=I(z)\,\mathbf h(x,y)$. V and I then obey the telegrapher equations with propagation constant β, so every mode is a transmission line and all of [03](../03-transmission-lines-matching/telegrapher-equations-characteristic-impedance.md) applies. Only the power $\tfrac12\mathrm{Re}\,VI^*$ is physical; how it is split between V and I is a choice. Pozar normalises so that $Z=Z_{TE}$. The classical alternatives for TE10 use V = ∫E_y dy along the centre line and I = the longitudinal broad-wall current:

| Definition | Formula | WR-90, 10 GHz |
|---|---|---|
| wave impedance | $Z_{TE}=k\eta/\beta$ | 499.0 Ω |
| power–voltage | $Z_{PV}=V^2/2P=(2b/a)Z_{TE}$ | 443.5 Ω |
| power–current | $Z_{PI}=2P/I^2=(\pi^2b/8a)Z_{TE}$ | 273.6 Ω |
| voltage–current | $Z_{VI}=V/I=(\pi b/2a)Z_{TE}$ | 348.3 Ω |

The ratios (Γ, S-parameters) at a junction are definite; absolute "waveguide ohms" are not. The b-proportional forms explain why a step in guide height alone reflects roughly $(b_2-b_1)/(b_2+b_1)$ (plus a step reactance), and why reduced-height guides are used in transitions.

**E. Exciting a guide: probes, loops and holes.** Modes are orthogonal, so a current $\mathbf J$ inside the guide excites mode n with amplitudes $A_n^\pm=-\frac{1}{P_n}\int\mathbf e_n^\mp\cdot\mathbf J\,dV$, $P_n=2\int\mathbf e_n\times\mathbf h_n\cdot\hat z\,dS$ (Pozar §4.7 [1]). For a transverse probe with current $I(s)$ and a short a distance l behind it, the radiated power gives the **input resistance**
$$R_\text{in}=\frac{2\sin^2(\beta l)}{P_n}\Big|\int\mathbf e_n\cdot\hat s\,\frac{I(s)}{I_0}\,ds\Big|^2\ \xrightarrow{\text{TE}_{10},\ \text{uniform }I,\ \text{length }d}\ \frac{2Z_{TE}d^2\sin^2\beta l}{ab}.$$
- **Electric probe:** along E, at an E maximum (centre of the broad wall), $\lambda_g/4$ in front of the short ($\sin\beta l=1$). WR-90 at 10 GHz: a 5 mm probe with uniform current gives 107 Ω. With the realistic open-tip current $I\propto\sin k(h-s)$, **R = 50 Ω at h = 5.9 mm = 0.58b**, the same as the 0.55b starting value in the openEMS horn tutorial. The probe *reactance* comes from the evanescent higher modes and is not computed here. In practice it is tuned out with probe length, a thicker probe or the back-short position.
- **Magnetic loop:** its axis along $\mathbf H$, placed where H is strong. At the short-circuit wall E = 0 and H is maximum, so loops go on the back wall and probes $\lambda_g/4$ away.
- **Small holes (Bethe):** a hole couples through its electric ($\tfrac23r^3$) and magnetic ($\tfrac43r^3$) polarisabilities, driven by the normal E and tangential H on the wall. Two holes λg/4 apart give a directional coupler. See [Green's functions Level 3b E](greens-functions-and-integral-equations.md) for the free-space transmission of a hole.

**F. Cylindrical cavities.** TM010 ($E_z=J_0(2.405\rho/R)$) has $f=2.4048c/(2\pi R)$ *independent of length*. Its Q is $Q_c=\frac{\eta p_{01}}{2R_s}\frac{1}{1+R/d}$: for R = 45 mm and d = 60 mm in copper, 2.5498 GHz and **Q_c = 19 650** (closed form = energy/loss integration). TE011 of the same can is at 4.769 GHz with **Q_c ≈ 41 000** (numerical). No TE011 current crosses the side-wall/end-plate joint, so a non-contacting tuning plunger does not spoil it: this is the classic wavemeter and dielectric-measurement mode ([permittivity measurement](../17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical value |
|---|---|---|
| f_c(TE10) = c/(2a√εr) | rectangular | WR-90: 6.557 GHz |
| Single-mode band ≈ 1.25–1.9 f_c | a = 2b | WR-90: 8.2–12.4 GHz |
| λ_g = λ/√(1−(f_c/f)²) | above cutoff | WR-90 @10 GHz: 39.7 mm |
| v_p v_g = c²/εr | hollow/filled guide | v_g = 0.755c (WR-90 @10 GHz) |
| α_c(TE10) (Pozar 3.96) | copper, smooth | 0.11 dB/m WR-90 @10 GHz |
| Below cutoff: 27.3 dB per a (rect.), 32 dB per diameter (circ.) | f ≪ f_c | vents |
| f_c(TE11 circular) = 1.8412c/(2πR) | circular | R = 10 mm: 8.79 GHz |
| Q_c ∝ (volume/surface)/δ | cavities | Cu, 2.45 GHz, 87 mm box: 15 600 |
| 1/Q0 = 1/Q_c + tanδ | filled cavity | tanδ 1e-4 caps Q at 10⁴ |
| Plane pair: f_mn = (c/2√εr)√((m/A)²+(n/B)²), Q ≈ 1/(tanδ + δ/h) | PCB | 100×50 mm FR-4: 715 MHz, Q ≈ 30 |
| SIW a_eff ≈ w − d²/(0.95s), s ≤ 2d | via-wall guide | RO4003C, w 20 mm: f_c 4.1 GHz |
| Circular single-mode band f_c(TE11)…1.306 f_c | circular | 90 mm can: 1.952–2.550 GHz |
| α_c TE_nm = R_s(k_c² + n²k²/(p′²−n²))/(Rkηβ); TM = R_s k/(Rηβ) | circular, smooth wall | 90 mm can, 2.45 GHz: 0.012 dB/m Cu, 0.029 tin |
| Parallel plate f_c,n = nc/(2d√εr) | plates | 0.2 mm FR-4: 357 GHz |
| Transverse resonance Z→ + Z← = 0 | layered cross-section | slab-loaded guide, surface waves |
| TM0 surface wave β/k0 ≈ 1 + ½[k0h(1−1/εr)]² | thin grounded slab | 1.43 mm FR-4, 433 MHz: 1 + 5.1×10⁻⁵ |
| Z_PV, Z_PI, Z_VI = (2b/a, π²b/8a, πb/2a)·Z_TE | TE10 | WR-90 10 GHz: 444 / 274 / 348 Ω |
| R_in = 2Z_TE d² sin²βl/(ab) | thin probe, uniform current | WR-90 5 mm probe: 107 Ω |
| TM010 f = 2.405c/(2πR); Q_c = ηp01/(2R_s(1+R/d)) | cylindrical cavity | R 45, d 60 mm Cu: 2.55 GHz, 19 650 |

## Worked examples

**1. A 2.45 GHz waveguide feed.** Operating ≥ 1.25 f_c needs f_c ≤ 1.96 GHz, and single-mode needs
f_c(TE20) = 2f_c > 2.45 GHz, i.e. 1.23 GHz < f_c < 1.96 GHz. WR-430 (f_c 1.372 GHz, TE20 2.745 GHz) fits; β at 2.45 GHz gives λ_g =
122.4/√(1 − (1.372/2.45)²) = 147.8 mm. Loss is ~0.009 dB/m — negligible.

**2. Why not waveguide at 433 MHz?** WR-2300 is 584 × 292 mm. A 3 m run of low-loss 1/2″ coax at
433 MHz loses roughly 0.1–0.2 dB (03 domain) — waveguide's advantage doesn't justify its size.

**3. Shield-can ventilation for a 915 MHz transmitter module.** Holes 3 mm in diameter in a 0.3 mm can:
f_c(TE11) = 58.6 GHz, cutoff attenuation per 0.3 mm depth ≈ 32 × 0.3/3 ≈ 3 dB — the real leakage is by
aperture coupling, which for 3 mm holes at 915 MHz (λ = 328 mm) is small (aperture ≪ λ/10). Holes
become a problem only when their size approaches ~λ/20–λ/10 at the frequencies of concern (EMC
harmonics!).

**4. Plane-pair resonance near LoRa 915 MHz.** A 120 × 80 mm four-layer flight computer, FR-4:
TM10 = c/(2·0.12·2.098) = 596 MHz, TM01 = 894 MHz, TM11 = 1.07 GHz. The TM01 mode at ~894 MHz sits
close to the 915 MHz band: expect elevated coupling from digital noise into the radio's supply/ground at
that frequency unless the planes are well stitched/decoupled or the board edge is lossy.

**5. Cantenna feed for 2.45 GHz, from the theory.** A 90 mm can: TE11 cutoff 1.952 GHz, TM01 2.550 GHz (cut off, but only 4 % above the operating frequency), $\lambda_g$ = 122.4/√(1 − (1.952/2.45)²) = 202.5 mm. Put the back of the can (the short) **λg/4 = 50.6 mm** behind the probe, not λ0/4 = 30.6 mm. Mount the probe radially from the wall, at the E maximum of the TE11 polarisation you want. With an open-tip current the mode-orthogonality integral gives R = 2, 13, 24 and 46 Ω for probe lengths 10, 20, 25 and 30.6 mm, and **50 Ω at 31.2 mm**, so the folk rule "probe = λ0/4" is right for the resistance; trim the length on a VNA to null the reactance. Make the can at least ≈ 3λg/4 ≈ 150 mm long so the evanescent TM01 and other fields from the probe decay before the mouth. Copper or tin wall loss is 0.01–0.03 dB/m and irrelevant; the open-end match and pattern follow [the horn page](../08-antennas/horn-reflector-aperture-antennas.md) and the open-ended-guide results in [Green's functions Level 3b D](greens-functions-and-integral-equations.md).

## Practical notes
- Waveguide flanges and joints need good contact across the broad walls (current flows across them for
  TE10); choke flanges tolerate small gaps.
- Coax-to-waveguide transitions use a probe λ_g/4 from a back short; SIW uses tapered microstrip.
- In enclosures, add RF absorber (lossy ferrite/carbon sheet) to kill box resonances rather than trying
  to move them.
- Microwave-oven cavities (2.45 GHz) are multimode (dimensions of several λ); mode stirrers average
  the standing-wave pattern.

- Measuring εr/tanδ by cavity perturbation, and extracting Q0 from loaded Q and coupling: [permittivity measurement](../17-test-measurement/resonator-and-cavity-perturbation-permittivity-measurement.md).
## Common mistakes & misconceptions
- **"Phase velocity > c violates relativity."** Only the pattern moves faster; energy and information
  travel at v_g < c.
- **"A waveguide works at any frequency above cutoff."** Above the next mode's cutoff, multiple modes
  propagate at different speeds — dispersion and mode conversion. Stay in the single-mode band.
- **"Small holes let no RF through."** Holes attenuate by cutoff only if they are *deep* (tube-like);
  thin-wall holes leak by aperture coupling, rising steeply with hole size/λ.
- **"The TE10 wave impedance is 377 Ω."** Z_TE = η/√(1 − (f_c/f)²) — 499 Ω in WR-90 at 10 GHz.
- **"PCB planes are just big capacitors."** Above the first cavity mode (hundreds of MHz for typical
  boards) they are resonators.
- **Using the free-space cutoff for a dielectric-filled guide or SIW.** Divide by √εr.
- **"A circular guide has a 2 : 1 single-mode band like WR guides."** Only 1.31 : 1 (TE11 to TM01).
- **Placing a cantenna probe λ0/4 from the back.** The short must be λg/4 away (50.6 mm in a 90 mm can at 2.45 GHz, not 30.6 mm); near cutoff λg ≫ λ0.
- **Quoting "the" impedance of a waveguide.** $Z_{TE}$, $Z_{PV}$, $Z_{PI}$ and $Z_{VI}$ differ by up to 1.8× for WR-90. Use ratios (Γ, S) or state the definition.
- **Ignoring the TE11 polarisation degeneracy.** A dented can or an off-axis probe excites both polarisations; the CP or linear purity of a circular feed depends on symmetry.

## How to simulate / verify
- `python3 tools/verify/em_waveguides.py` — cutoffs for WR-2300…WR-90 and circular modes (Bessel zeros);
  TE10 dispersion with numeric group velocity; α_c closed form vs numeric wall-loss integral;
  below-cutoff attenuation; cavity TE101 f0 and Q_c (closed form vs numeric energy/loss); PCB plane-pair
  modes and Q; SIW equivalent width.
- openEMS provides rectangular-waveguide ports (`AddRectWaveGuidePort`) — simulate a WR-90 section and
  compare α and λ_g with the formulas; eigenmode-like cavity analysis via ring-down in FDTD.
- scikit-rf `RectangularWaveguide` media object computes β, Z and loss for TE/TM modes.
- `python3 tools/verify/s5_waveguide_extras.py` (≈ 5 s, W5-S5, 14/14 checks): circular-guide Bessel zeros and α_c closed forms vs wall-loss integrals; TE10 modal V/I definitions; parallel-plate cutoffs and TEM loss; transverse resonance for grounded-slab surface waves (cross-checked with `e11_greens.py` and the 12 domain) and for a slab-loaded WR-90 vs a finite-difference eigen-solver; TM010/TE011 cavity Q; probe resistance by mode orthogonality and the cantenna probe length.

## Open questions / gaps
- SIW design rules (s ≤ 2d, d < λ_g/5) are quoted from knowledge of Deslandes & Wu; leakage and
  radiation loss formulas (Bozzi et al.) not included.
- Measured plane-pair resonance Q including edge radiation for typical 4-layer boards — 13-pcb domain.
- Probe and loop *reactance* (higher-order evanescent modes) is not computed; only the input resistance is. A full-wave (openEMS) cantenna S11 would close this.
- The TE011 Q (≈ 41 000) is numerical only (field integration with an internal energy-balance check); no closed form was cross-checked.

## Sources
1. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §3.1 (general TE/TM/TEM solutions), §3.3
   (rectangular waveguide, eq. 3.96 TE10 attenuation), §3.4 (circular waveguide, Bessel zeros), §6.3–6.4
   (rectangular and cylindrical cavities, Q of TE10ℓ, eq. 6.46). (textbook)
2. S. Ramo, J. R. Whinnery, T. Van Duzer, *Fields and Waves in Communication Electronics*, 3rd ed.,
   1994, ch. 8 (waveguides; plane-wave "zig-zag" picture; group velocity), ch. 10 (cavity resonators).
   (textbook)
3. R. E. Collin, *Foundations for Microwave Engineering*, 2nd ed., IEEE Press/Wiley 2001, ch. 3
   (waveguides), ch. 7 (cavities). (textbook; cited from knowledge)
4. R. P. Feynman et al., *Feynman Lectures on Physics* Vol. II, ch. 23 (cavity resonators) and ch. 24
   (waveguides: "the waveguide as a transmission line"; phase vs group velocity). (textbook, free;
   cited from knowledge)
5. Y. Cassivi, L. Perregrini, P. Arcioni, M. Bressan, K. Wu, G. Conciauro, "Dispersion characteristics of
   substrate integrated rectangular waveguide," *IEEE Microw. Wireless Compon. Lett.* 12(9), 333–335, 2002
   (a_eff = w − d²/(0.95s)). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
6. D. Deslandes and K. Wu, "Accurate modeling, wave mechanisms, and design considerations of a
   substrate integrated waveguide," *IEEE Trans. MTT* 54(6), 2516–2526, 2006 (design rules). (peer-reviewed;
   bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
7. EIA/IEC waveguide designations (WR-xx = inner width in hundredths of an inch; WR-90 0.900 × 0.400 in).
   (standard; widely tabulated)
8. N. Marcuvitz, *Waveguide Handbook*, MIT Rad. Lab. Series vol. 10, 1951 (IEE reprint 1986), ch. 1–2 (modal V/I and transmission-line representation, transverse resonance, impedance definitions). (textbook; cited from knowledge)
9. R. E. Collin, *Field Theory of Guided Waves*, 2nd ed., IEEE Press 1991, ch. 5 (transverse resonance, partially filled guides), ch. 7 (probe/loop/aperture excitation, Bethe small holes). (textbook; cited from knowledge)
10. Verification: `tools/verify/em_waveguides.py`, `tools/verify/s5_waveguide_extras.py`. (numerical check)
