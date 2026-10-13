---
title: Planar arrays, element patterns and mutual coupling — lattices, active element pattern, active reflection coefficient, scan blindness, embedded element efficiency
domain: 12-phased-arrays
slug: planar-arrays-element-pattern-coupling
tags: [planar-array, rectangular-lattice, triangular-lattice, u-v-space, active-element-pattern, embedded-element-pattern, mutual-coupling, active-reflection-coefficient, scan-impedance, scan-blindness, surface-wave, floquet, hannan, embedded-element-efficiency, edge-effects, small-arrays, conformal-arrays]
prerequisites: [array-factor-linear-arrays.md, beam-steering-grating-lobes.md, ../08-antennas/antenna-fundamentals.md, ../03-transmission-lines-matching/reflections-vswr-return-loss-mismatch.md]
related: [tapering-sidelobe-control.md, array-calibration.md, adaptive-beamforming-doa.md, beamforming-architectures.md, diy-phased-array-projects.md, ../08-antennas/patch-antennas.md, ../08-antennas/dipoles-and-monopoles.md, ../08-antennas/antennas-on-rockets.md, ../08-antennas/antenna-simulation-nec-openems.md, ../03-transmission-lines-matching/s-parameters.md, ../16-simulation-tools/openems-workflow.md, ../17-test-measurement/vna-fundamentals-calibration.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Planar arrays, element patterns and mutual coupling

## Questions this page answers
- How do I steer a 2-D (planar) array in azimuth and elevation?
- Should I put the elements on a square grid or a triangular grid?
- My patch is perfectly matched on its own — why is it mismatched once it's in the array, and why does the match change as I steer?
- What is the difference between the isolated element pattern, the embedded (active) element pattern and the array factor?
- What is "active reflection coefficient" (scan impedance) and how do I measure it with an ordinary 2-port VNA?
- What is scan blindness, and will my FR-4 patch array suffer from it?
- Why is the gain of an array less than N × the gain of one element (the element-gain paradox)?
- What is the maximum gain one element can contribute in a big array?
- Do edge elements behave differently? What changes for a small (4–16 element) array?
- How strong is the coupling between two λ/2 dipoles or patches half a wavelength apart?
- Is closer spacing always safer?
- How does coupling affect a direction-finding array?

## TL;DR
- **2-D array factor**: with u = sinθcosφ, v = sinθsinφ, steering phases φ_mn = −k(x_m u₀ + y_n v₀). A rectangular grid is separable: AF = AF_x(u − u₀)·AF_y(v − v₀). Visible space is the unit circle u² + v² ≤ 1; grating lobes form a lattice around the beam (the reciprocal lattice of the element grid).
- **Triangular (hexagonal) lattice** needs **13.4% fewer elements** than a square one for the same grating-lobe-free scan cone (Sharp 1961 [6]; verified): square d ≤ λ/(1+sinθ_m); equilateral-triangle side b ≤ 2λ/(√3(1+sinθ_m)) (±45°: 0.586λ vs 0.676λ).
- **Gain of a large planar array**: G(θ₀) = (4πA/λ²)·η_taper·cosθ₀·(1 − |Γ_a(θ₀)|²). Each element can contribute at most **4πA_cell/λ²** (Hannan [4]) — π (4.97 dBi) for a λ/2 × λ/2 cell. An 8 × 8 array of cosθ (6 dBi) elements at λ/2 gives 23.04 dBi = Hannan's 23.03 dBi, not 10 log 64 + 6 = 24.08 dBi.
- **Embedded element efficiency** e_emb = 1 − Σ_i |S_im|² (power lost into the other ports' loads) [5]; its dense-array ceiling is π·d_x d_y/λ² (79% at λ/2 × λ/2; ≤ 50% at 0.4λ × 0.4λ). This is the "element-gain paradox": the array's realized gain equals the *sum of the embedded* realized gains, not of the isolated ones.
- **Active reflection coefficient** of element m: Γ_a,m(θ₀) = Σ_n S_mn·a_n/a_m. It changes with scan because the coupled waves add with scan-dependent phases. MoM example (8 λ/2 dipoles at λ/2 over a λ/4 reflector, matched in isolation): |Γ_a| = 0.13 broadside, 0.29 at 45°, 0.63 at 60°, 0.77 at 75° (VSWR 1.3 → 1.8 → 4.4 → 7.7). Scan loss −0.7 / −2.2 / −6.8 dB at 45 / 60 / 75°.
- **Active (embedded) element pattern** — one element driven, all others terminated — *contains* the scan loss: for a large array, G_array(θ₀) = N·G_emb(θ₀) (Hannan, Pozar [4][7]). Measure one embedded pattern near the array centre and you have predicted the scan performance.
- **Scan blindness** in printed arrays: a Floquet (scan) mode phase-matches a substrate surface wave; the estimate is **sinθ_b ≈ λ/d − β_sw/k₀** (E-plane), always *before* grating-lobe onset. 1.6 mm FR-4 at 5.8 GHz (β_TM0/k₀ = 1.012): d = λ/2 → ≈81° (harmless), d = 0.586λ (the "±45° grating-lobe limit") → ≈44° (right at the edge of scan!). A full-wave finite-row check (openEMS, 15 patches, 2026-10-13) put a shallow 2–3 dB embedded-pattern dip near **52°** rather than 44°, and none at λ/2 — the spacing rule stands, the angle is an estimate. Safer spacing rule for printed arrays: **d ≤ λ/(β_sw/k₀ + |sinθ_max|)**.
- **Small arrays are all edge**: in an 8-element dipole array the edge element's embedded gain at 30° is 1.4 dB below the centre element's (MoM). Pattern multiplication with the isolated element pattern is only a first approximation.

## Intuition (no math)

**An element inside an array is a different antenna.** Put a patch alone on a board and it has one impedance and one pattern. Surround it with identical patches half a wavelength away and part of what it radiates is picked up by its neighbours and re-radiated (or absorbed in their loads). Its impedance changes, and its pattern changes — typically narrower toward the horizon and rippled. The pattern of *one* element measured *in place*, with all the others connected to their 50 Ω loads, is the embedded (or "active") element pattern; this — not the stand-alone pattern — is what you multiply by the array factor.

**Why the match changes with scan.** When every element is driven, element m receives, besides its own reflection, a little wave from every other element through the coupling S_mn. These little waves arrive with phases set by the steering phases. At one scan angle they might largely cancel (good match); at another they add up (poor match). So "the" impedance of an array element is really a function of the scan angle: the *scan impedance* or *active impedance*. Many small couplings can add to a large reflection: four neighbours at −15 dB and four diagonals at −22 dB can sum coherently to |Γ| ≈ 1.

**Hannan's paradox, as energy bookkeeping.** An element alone may have 6–7 dBi. Yet you can't put 64 of them in a 4λ × 4λ square and get 64 × 6 dBi, because the aperture area caps the gain at 4πA/λ². Where did the missing gain go? When one element is driven in the array, some of its power flows into the neighbours' loads — it is not radiated. That "coupled-away" power is exactly the gap. Nothing is violated: each element simply cannot be as efficient in the crowd as alone.

**Why gain falls off with scan in a flat array.** A flat aperture viewed from an angle looks smaller (area × cosθ). The embedded element pattern of a well-designed dense array follows that cosθ; on top, the active mismatch removes some power. Measured scan loss is therefore "projected area" plus "mismatch".

**Scan blindness is a resonance.** A dielectric substrate on a ground plane can guide a surface wave that skims along the board. When you steer the beam, the phase progression across the array launches waves that travel along the board at a certain phase speed. If that speed matches the surface wave's, the array pours its power into the substrate instead of into space: at that angle the array goes "blind" (|Γ_a| → 1). Thick, high-permittivity substrates and wide spacing make it happen at smaller angles.

## The math

### Level 1 — definitions and working formulas

Planar array in the x–y plane, normal z, elements at (x_m, y_n). Direction cosines u = sinθcosφ, v = sinθsinφ. Steering to (θ₀, φ₀): u₀ = sinθ₀cosφ₀, v₀ = sinθ₀sinφ₀.
$$AF(u,v) = \sum_{m,n} a_{mn}\,e^{jk[x_m(u-u_0)+y_n(v-v_0)]}\ \xrightarrow{\text{rect. grid, separable }a_{mn}=a_m b_n}\ AF_x(u-u_0)\,AF_y(v-v_0).$$

| Quantity | Formula | Notes |
|---|---|---|
| Steering phase | φ_mn = −k(x_m sinθ₀cosφ₀ + y_n sinθ₀sinφ₀) | modulo 2π |
| Grating lobes (rect.) | (u₀ + pλ/d_x, v₀ + qλ/d_y) | p, q integers ≠ (0,0) |
| No GL in cone θ_m (square) | d ≤ λ/(1+sinθ_m) | ±60° → 0.536λ |
| No GL in cone θ_m (equilateral triangle, side b) | b ≤ 2λ/(√3(1+sinθ_m)) | ±60° → 0.619λ; 13.4% fewer elements |
| Large-array gain | G ≈ (4πA/λ²) η_t cosθ₀ (1 − \|Γ_a\|²) | A = physical area (N·A_cell) |
| Max embedded element gain | G_emb ≤ (4πA_cell/λ²) cosθ | Hannan |
| Embedded element efficiency | e_emb,m = 1 − Σ_i \|S_im\|² (lossless) | ≤ πd_x d_y/λ² when d_x, d_y < 0.56λ |
| Active reflection coefficient | Γ_a,m = Σ_n S_mn a_n/a_m | a_n = incident waves (drive) |
| Active impedance | Z_a,m = Σ_n Z_mn I_n/I_m | same thing in Z form |
| Scan blindness (estimate) | sinθ_b = λ/d − β_sw/k₀ | E-plane, printed arrays |

Beamwidths of a rectangular aperture L_x × L_y scanned in the x–z plane: ≈0.886λ/(L_x cosθ₀) in the scan plane and ≈0.886λ/L_y across it (uniform illumination).

### Level 1½ — a planar array with algebra only
- **Gain comes from area.** A large array behaves like an aperture of area $A$ (the elements times the cell each one occupies). Its gain is $G \approx 4\pi A/\lambda^2$. With half-wave spacing each cell is $\lambda^2/4$, so $G \approx \pi N$ for $N$ elements: doubling the element count adds 3 dB.
- **Scanning shrinks the area you see.** Looking at the array from θ₀ off broadside, its projected area is $A\cos\theta_0$. Gain and beam narrowness both fall by $\cos\theta_0$, which is −1.5 dB at 45° and −3 dB at 60°. Real elements usually lose a little more, because of mismatch from mutual coupling (Level 2).
- **Spacing sets the grating lobes.** Steering adds the phase $kd\sin\theta_0$ per element. A second, unwanted beam (a grating lobe) appears where the extra path from one element to the next is a whole wavelength. Keeping it out of real space while scanning to θ_m needs $d \le \lambda/(1+\sin\theta_m)$. A triangular lattice relaxes this, so it needs about 13 % fewer elements.
- **The 2-D pattern is two 1-D patterns multiplied.** With row and column weights that separate, $AF = AF_x \times AF_y$, so every [linear-array](array-factor-linear-arrays.md) result applies to each axis.

*Worked numbers (verified, `tools/verify/s18_level15_numbers.py`).* An 8 × 8 patch array at 5.8 GHz with λ/2 = 25.8 mm spacing (a 207 mm square):
- **Gain:** $G \approx \pi\times64$ = 201, i.e. **23.0 dBi** before losses.
- **Scan loss:** at 45° scan it falls to 21.5 dBi.
- **Spacing limit:** scanning to ±60° without grating lobes needs $d \le$ 27.7 mm, so λ/2 has 2 mm to spare.

### Level 2 — derivations

**(a) The 2-D array factor.** From the general form AF(û) = Σ w_i e^{jkû·r_i} ([array factor](array-factor-linear-arrays.md)) with r_i = (x_m, y_n, 0): û·r_i = x_m sinθcosφ + y_n sinθsinφ = x_m u + y_n v. Steering weights w_mn = a_mn e^{−jk(x_m u₀ + y_n v₀)}. For a rectangular grid and separable amplitudes the double sum factorises into two linear-array factors, so all the linear-array results (beamwidth, sidelobes, tapers) apply along each axis. Note that separable tapers give low sidelobes only along the principal planes; diagonal cuts get the *product* of two sidelobes (very low), whereas circularly symmetric tapers treat all cuts equally ([tapering](tapering-sidelobe-control.md)).

**(b) Grating-lobe lattice and the triangular saving.** The AF is periodic in (u, v) with the *reciprocal lattice* of the element lattice: if a₁, a₂ are primitive lattice vectors, the replicas sit at (u₀, v₀) + λ(p b₁ + q b₂) with a_i·b_j = δ_ij. Scanning anywhere inside a cone sinθ ≤ s keeps all replicas outside the visible unit circle if the nearest reciprocal-lattice point is farther than 1 + s. Square lattice: nearest point at λ/d → d ≤ λ/(1+s), cell area d² = λ²/(1+s)². Equilateral triangular lattice of side b: the reciprocal lattice is hexagonal with nearest-point distance 2λ/(√3 b) → b ≤ 2λ/(√3(1+s)), cell area (√3/2)b² = (2/√3)λ²/(1+s)². Ratio of cell areas 2/√3 = 1.1547, so the triangular grid needs 1/1.1547 = 0.866 as many elements: **13.4% saving** for any cone (Sharp [6]; `tools/verify/array_planar.py` A1, analytic and brute-force agree). The triangular grid also packs square patches less conveniently and complicates feed routing — the saving matters most for large, expensive arrays.

**(c) Mutual coupling as an N-port.** Treat the array's feed terminals as an N-port with impedance matrix Z (V = Z I) or scattering matrix S (b = S a, a = incident, b = reflected waves at reference Z₀). When all ports are driven with incident waves a_n (the beamformer's amplitudes and steering phases), the wave reflected at port m is b_m = Σ_n S_mn a_n, so the reflection that port *sees* is
$$\Gamma_{a,m} = \frac{b_m}{a_m} = \sum_n S_{mn}\frac{a_n}{a_m} = S_{mm} + \sum_{n\ne m}S_{mn}\,\frac{|a_n|}{|a_m|}\,e^{j(\phi_n-\phi_m)} .$$
The coupling terms add with the steering phase difference: this is the scan dependence. Equivalently Z_a,m = V_m/I_m = Σ_n Z_mn I_n/I_m. **Measuring it**: with a 2-port VNA, measure S_mn for element m against every n (all other ports terminated in Z₀), then evaluate the sum for each scan angle in software. No multiport drive is needed.

**(d) Embedded (active) element pattern and superposition.** Define E_m^emb(û) as the far field when port m is driven by a unit incident wave and every other port is terminated in Z₀. Because the structure is linear, the field for any drive vector a is exactly
$$\mathbf E(\hat u) = \sum_m a_m\,\mathbf E^{emb}_m(\hat u) .$$
This is exact (all coupling is contained in the embedded patterns); pattern multiplication is the special case E_m^emb(û) ≈ E^emb(û)e^{jkû·r_m} valid for elements far from the edges of a large array. The MoM model (script B4) confirms: for 8 λ/2 dipoles scanned to 30°, the exact pattern and "isolated element × AF" agree on the beam direction, but the highest sidelobe differs (−12.5 vs −12.8 dB) and edge-element patterns differ from centre ones by >1 dB.

**(e) Why the embedded pattern predicts scan loss (Hannan/Pozar).** Drive all N elements of a large array with |a_n| = 1 and the scan phase for θ₀. The available power is N·P_av, of which N·P_av(1 − |Γ_a(θ₀)|²) is accepted. A large aperture of area A = N·A_cell scanned to θ₀ has directivity 4πA cosθ₀/λ² (projected area, no grating lobes), so its realized gain is G_R = (4πA cosθ₀/λ²)(1 − |Γ_a|²). By superposition the peak field is N times one embedded element's field in that direction, so the power density is N² times, while the available power is N times: G_R = N·G_emb(θ₀). Therefore
$$G_{emb}(\theta) = \frac{4\pi A_{cell}}{\lambda^2}\cos\theta\,\big(1-|\Gamma_a(\theta)|^2\big)$$
[4][7]. For λ/2 × λ/2 cells, 4πA_cell/λ² = π = 4.97 dBi: the ceiling for any element in a dense λ/2 array. The script's 8 × 8 array of cosθ elements (A2) gives 23.04 dBi at broadside against 4πA/λ² = 23.03 dBi, and tracks 4πA cosθ₀/λ² within 0.25 dB to 60° scan.

**(f) Embedded element efficiency (the element-gain paradox).** With one port driven and the rest terminated, the power not radiated is the power reflected at the driven port plus that delivered to the other loads: e_emb,m = 1 − Σ_i |S_im|² (lossless structure) [5]. Integrating (e) over the hemisphere with |Γ_a| = 0 in visible space gives Hannan's asymptote e_emb ≤ π d_x d_y/λ² for d_x, d_y < 1/√π·λ = 0.56λ [4][5]: 0.785 (−1.05 dB) at λ/2, 0.50 (−3 dB) at 0.4λ, 0.13 (−9 dB) at 0.2λ (script A3). For an *infinite* periodic array it also equals 1 − (1/π²)∬|Γ_a(γ_x, γ_y)|² dγ_x dγ_y over all inter-element phases — including the "invisible" phases where the array cannot radiate and |Γ_a| ≈ 1, which is why dense arrays have low embedded efficiency [5]. In the MoM dipole array (B3), e_emb = 0.906 (centre) and 0.946 (edge) in free space, 0.884 / 0.930 over the reflector; the S-matrix value and the radiated-power integral agree to three decimals.

**(g) Scan blindness in printed arrays.** Scanning with inter-element phase kd sinθ₀ excites Floquet modes with transverse wavenumbers k_x = k₀ sinθ₀ + 2πp/d. A grounded dielectric slab supports a TM₀ surface wave (no cutoff) with β_sw slightly larger than k₀. When a Floquet mode's |k_x| equals β_sw, the scan excitation is phase-matched to the surface wave and power couples into it: the active reflection coefficient approaches 1. For p = −1: k₀ sinθ_b − 2π/d = −β_sw, so
$$\sin\theta_b \approx \frac{\lambda}{d} - \frac{\beta_{sw}}{k_0}\qquad(\text{grating-lobe onset: } \sin\theta_{GL} = \lambda/d - 1).$$
Pozar & Schaubert introduced and validated this Floquet–surface-wave explanation with MoM and waveguide-simulator measurements [8]; the true blind angle sits close to (typically slightly inside) this estimate because the elements load the surface wave.

*Full-wave finite-row check (W5-S11, 2026-10-13; `tools/verify/sim2_openems_array_blindness.py`, [openEMS workflow Run 5](../16-simulation-tools/openems-workflow.md)).* openEMS has no phase-shifted periodic boundary, so the infinite-array unit cell cannot be built there. Instead, a 15-element E-plane row of probe-fed 5.8 GHz patches on 1.6 mm FR-4 (εr 4.4, lossless, slab running into PML) was simulated with the centre element driven and the others terminated in 50 Ω; by Hannan's relation its embedded pattern ∝ (1 − |Γ_a(θ)|²) cos θ. Results: at d = 0.586λ a reproducible but **shallow (≈ 2–3 dB) E-plane dip centred near 52°** (residual −1.6 / −2.2 dB at 53° on coarse / fine mesh; the d = 0.586λ minus d = 0.5λ difference is −1.7 to −2.6 dB over 40–60°, ≈ 0 at 65°); at d = 0.5λ no dip ≥ 3 dB within 0–70°. **This disagrees with the 44° estimate above in two ways**: the dip is ≈ 8° *outside* the estimate (not slightly inside it, as Pozar & Schaubert's infinite-array results lead one to expect), and it is a shallow dip rather than a blindness (|Γ_a| → 1). The likely causes are finite size (one row only, edge elements not in an array environment) and element mismatch (the patches' S11 minimum sits at 5.2 GHz, not 5.8). The pre-registered prediction (A1: dip ≥ 3 dB within ±5° of 44°) therefore **missed**; A2 (no dip at λ/2) passed. The finite row supports the spacing rule qualitatively but does not give a quantitative Γ_a(θ) for an infinite array. β_TM0 from the grounded-slab dispersion relation k_c tan(k_c h) = ε_r α (k_c² = ε_r k₀² − β², α² = β² − k₀²) (script C1): 1.6 mm FR-4 (ε_r 4.4) → β/k₀ = 1.0020 at 2.45 GHz, 1.0121 at 5.8 GHz, 1.0436 at 10.25 GHz; 3.2 mm FR-4 at 10.25 GHz → 1.289; 0.762 mm RO4350B at 5.8 GHz → 1.0023. Consequences: blindness estimates for λ/2 spacing are 81° (FR-4 1.6 mm, 5.8 GHz), 73° (same, 10.25 GHz) and 45° (3.2 mm FR-4, 10.25 GHz). E-plane scanning is the dangerous plane for TM₀; H-plane blindness needs a TE₁ surface wave, which only exists above h ≈ λ/(4√(ε_r − 1)).

### Level 3 — general theory and limits

- **Infinite-array (Floquet) analysis** is the standard design tool: simulate one unit cell with periodic (phase-shift) boundaries and get Γ_a(θ, φ) directly. Real finite arrays approach it a few elements in from the edge; edge rows need separate treatment (or dummy terminated elements around the active area).
- **Wheeler's current sheet** [9]: an infinite, continuous electric current sheet has scan resistance ∝ 1/cosθ in the E-plane and ∝ cosθ in the H-plane — so even an "ideal" array cannot stay matched with a fixed network. Hannan proved that, with sufficiently complex matching networks, an array *can* in principle be matched at all scan angles [10]; practical approximations are wide-angle impedance-matching (WAIM) dielectric sheets and inter-element coupling networks.
- **Coupling is not always bad.** Tightly coupled (connected) arrays exploit it for decade bandwidths; closely spaced DF arrays can be *decoupled* digitally by applying the inverse coupling matrix C⁻¹ to the element outputs (with C measured or simulated) — see [calibration](array-calibration.md) and [DOA](adaptive-beamforming-doa.md).
- **Receive DOA arrays**: coupling distorts the steering vector a(θ) → C·a(θ). Uncorrected, MUSIC/ESPRIT bearings acquire angle-dependent biases of degrees; the KrakenSDR's λ/2-ish spaced whips on a car roof are a textbook case where calibration or a coupling model matters.
- **Conformal arrays** (cylinders, a rocket body): elements point different ways, the embedded patterns are all different and pattern multiplication fails; the exact superposition of (d) still works. Useful context for wraparound rocket antennas ([antennas on rockets](../08-antennas/antennas-on-rockets.md)).
- **Superdirective / dense arrays**: below λ/2 spacing, embedded efficiency drops as πd²/λ²; directivity barely rises; realized gain may fall.

## Design equations & rules of thumb

| Rule | Validity | Typical value |
|---|---|---|
| Square grid d ≤ λ_max-f/(1+sinθ_m) | GL-free cone | ±45°: 0.586λ |
| Triangular side b ≤ 2λ/(√3(1+sinθ_m)) | GL-free cone | ±45°: 0.676λ, 13.4% fewer elements |
| Printed arrays: d ≤ λ/(β_sw/k₀ + sinθ_m) | TM₀ blindness margin | FR-4 1.6 mm @ 5.8 GHz, ±45°: 0.582λ |
| G ≈ 4πA cosθ₀ η_t (1−\|Γ_a\|²)/λ² | large array | 8 × 8 @ λ/2: 23.0 dBi broadside |
| G_emb ≤ π cosθ (λ/2 cells) | dense array | 4.97 dBi |
| e_emb ≤ πd_x d_y/λ² | d < 0.56λ | λ/2: 79%; 0.4λ: 50% |
| Γ_a,m = Σ S_mn a_n/a_m | any array | measure with 2-port VNA, sum in software |
| Coupling between λ/2 dipoles side by side at λ/2 | thin wire, free space | Z₁₂ ≈ −17.5 − j28.7 Ω, \|S₂₁\| ≈ −15 dB (MoM) |
| Scan loss of a real array at 60° | good design | 3–5 dB; poor design: blind angles |

## Worked examples

**Example 1 — an 8 × 8 5.8 GHz patch panel for a ground station.** λ = 51.69 mm. Square λ/2 grid (25.84 mm) → 207 × 207 mm aperture, 64 elements.
- Directivity ≈ 4πA/λ² = 4π(64 × 0.25) = 201 → **23.0 dBi** (cosθ embedded elements, verified A2). Not 10 log 64 + 6.5 = 24.6 dBi.
- Realized gain: minus patch efficiency (FR-4 1.6 mm patches ≈ 50–60% → −2.5 dB; RO4350B ≈ 80% → −1 dB, [patch antennas](../08-antennas/patch-antennas.md)), minus feed/beamformer loss. Expect ≈ 19–21 dBi on FR-4.
- Beamwidth 12.7° × 12.7° broadside; at 45° scan in one plane 18° × 12.7°. Gain at 45°: −1.5 dB (cos) − active mismatch (≈0.3–1 dB) ≈ −2 dB.
- If scan is limited to a ±45° cone: a square grid could open up to 0.586λ = 30.3 mm, but on 1.6 mm FR-4 the blindness estimate at that spacing is sinθ_b = 1/0.586 − 1.012 = 0.694 → **44°**, right at the edge of the scan cone. Use d ≤ λ/(1.012 + 0.707) = 0.582λ = 30.1 mm — or stay at λ/2 and accept 64 elements. A triangular grid with b ≤ 0.676λ (34.9 mm) covers the same aperture with ≈13% fewer elements (≈41 instead of ≈47 for the 0.586λ square grid) but its nearest-neighbour E-plane spacing must also respect the blindness margin.

**Example 2 — "I matched each element perfectly"; what the array sees.** 8 resonant λ/2 dipoles side by side at λ/2, λ/4 in front of a reflector, each matched to its *isolated* impedance (88.6 + j27.9 Ω; reference 88.6 Ω). MoM (script B2): |Γ_a| (centre element) = 0.13, 0.07, 0.07, 0.29, 0.63, 0.77 at 0, 15, 30, 45, 60, 75°. The realized gain falls −0.19, −0.73, −2.24, −6.82 dB at 30, 45, 60, 75° (cos alone: −0.62, −1.51, −3.01, −5.87 dB) — better than cos near 30–45° because the match *improves* there, much worse at 75°. On transmit, the PAs see VSWR 4.4 at 60° scan: check their load-pull/stability before scanning that far.

**Example 3 — neighbour coupling sums up.** From the MoM model, adjacent dipoles couple at −15.0 dB (|S₂₁| = 0.18) and next-neighbours at −22.1 dB (0.079). The worst-case coherent sum for a centre element with two neighbours each side is 2(0.18) + 2(0.079) ≈ 0.52 before any S_mm — comparable to the 0.44–0.63 actually seen at 60°. In a 2-D array with four nearest and four diagonal neighbours at similar levels, the coherent sum can approach 1: this is why "−15 dB isolation between patches" is not "negligible coupling".

**Example 4 — measuring Γ_a with a NanoVNA.** For a 4-element 2.45 GHz test array: measure S₂₂ (element 2's own reflection) and S₂₁, S₂₃, S₂₄ with the unused ports in 50 Ω loads (4 two-port sweeps). For a scan angle θ₀ and d = λ/2, compute Γ_a,2 = S₂₂ + S₂₁e^{+jπsinθ₀} + S₂₃e^{−jπsinθ₀} + S₂₄e^{−j2πsinθ₀} (signs follow a_n ∝ e^{−jkx_n sinθ₀}, element n at x = (n−1)d). Plot |Γ_a,2| vs θ₀ at each frequency: that is the array's scan match.

**Example 5 — small-array edge effects.** In the free-space 8-dipole model, the embedded realized gain at 30° is 2.41 dBi for the centre element and 1.03 dBi for the edge element (B3); the edge element also has higher embedded efficiency (0.946 vs 0.906) because it has neighbours on one side only. In a 4-element array every element is an edge element; patterns are asymmetric and the "N × embedded gain" rule is only approximate.

## Practical notes
- **Simulate a unit cell, then the finite array.** A full-wave tool with phase-shifted periodic (Floquet/Bloch) boundaries gives Γ_a(θ, φ) for the infinite array; then simulate the finite array (or a 5 × 5 patch of it) to see edge effects. **openEMS (v0.37) has no periodic boundary** (checked in its source: PEC, PMC, MUR, PML only), so with openEMS use the finite-array embedded-pattern route of [openEMS workflow Run 5](../16-simulation-tools/openems-workflow.md); for the unit cell use MEEP (Bloch-periodic boundaries) or a commercial/student code (CST, HFSS).
- **Dummy elements** around the edge (terminated in 50 Ω) make the active elements see a more uniform environment — cheap insurance for small arrays.
- **Substrate choice**: thin, low-ε_r substrates push blindness out; FR-4 at 1.6 mm is fine up to ≈6 GHz for λ/2 spacing, marginal at 10 GHz with 3.2 mm. Cavity-backed patches, shorting-pin fences, or EBG structures suppress surface waves.
- **Measure embedded element patterns** in an anechoic setup (or outdoors at > 2D²/λ) with all other ports loaded. A cheap DIY turntable + SDR works ([antenna measurement](../08-antennas/antenna-measurement.md), [OTA testing](../17-test-measurement/antenna-range-ota-testing.md)).
- **LNA/PA per element**: the active impedance is what each LNA sees as its source — its noise figure and stability depend on scan angle. Isolators or balanced amplifiers decouple this in high-end T/R modules.
- **DF arrays**: magnetic-mount whips on a car roof couple strongly and the roof is not an infinite ground plane; KrakenSDR's software calibrates the receivers but not the antenna coupling — expect a few degrees of bias unless you calibrate against known bearings ([calibration](array-calibration.md)).

## Common mistakes & misconceptions
- **"If each element is matched, the array is matched."** Only at the scan angle where the coupling terms happen to cancel. Design and measure the *active* reflection coefficient over the scan range.
- **"Isolated element pattern × array factor is exact."** It ignores coupling and edge effects; use the embedded element pattern, and the exact superposition for small arrays.
- **"Array gain = N × isolated element gain."** Capped by 4πA/λ² (Hannan); the difference is the embedded element efficiency.
- **"−15 dB coupling is negligible."** Several such terms add coherently at some scan angle.
- **"The grating-lobe rule guarantees clean scanning."** Printed arrays go blind *before* grating-lobe onset; use λ/(β_sw/k₀ + sinθ_m).
- **"Closer spacing is always safer."** It avoids grating lobes but lowers embedded efficiency (π d²/λ²), increases coupling and impedance variation, and needs more channels.
- **"Scan blindness is a far-field null I can fix with calibration."** It is an impedance (power-acceptance) failure; no weighting recovers it.
- **"Triangular grids are exotic."** They are standard in radar/SATCOM panels because they save 13.4% of the (costly) channels.

## How to simulate / verify
- `tools/verify/array_planar.py` (~70 s): lattice grating-lobe limits (analytic + brute-force reciprocal lattice), 8 × 8 directivity vs Hannan, Hannan asymptote table; thin-wire MoM (reusing `tools/verify/ant_mom_wire.py`) for an 8-dipole H-plane array in free space and over a PEC reflector: Z/S matrices, active reflection coefficient vs scan, embedded patterns and efficiencies (S-matrix vs pattern integral), exact superposition vs pattern multiplication, realized gain vs scan; TM₀ surface-wave β and blindness estimates for common substrates.
- Next step for a real design: a **unit-cell** model of the actual patch at 5.8 GHz with periodic boundaries (MEEP or CST/HFSS — not openEMS, which lacks them) to replace the phase-matching estimate with a computed Γ_a(θ). The finite-row openEMS model is `~/opt/openEMS/venv/bin/python tools/verify/sim2_openems_array_blindness.py` (d0586, d05, single, *_fine cases; 43–128 s each).
- NEC-2 handles wire/dipole/Yagi arrays with full coupling ([NEC/openEMS](../08-antennas/antenna-simulation-nec-openems.md)).

## Open questions / gaps
- No computed or measured Γ_a(θ) for an actual FR-4 patch array at 5.8 GHz yet; the blindness angles here are Floquet phase-matching *estimates* (medium confidence). The only full-wave result is the 15-element finite row (dip ≈ 52°, 2–3 dB deep vs the 44° estimate); an infinite-array unit cell (MEEP/commercial) or a larger 2-D finite array is still needed (register G-16-06).
- Typical measured patch-to-patch coupling on FR-4 (E- vs H-plane) at 2.4/5.8 GHz not yet sourced; only the dipole MoM values are verified.
- Mailloux ch. 6 ("Summary of element pattern and mutual impedance effects") and Hansen's mutual-coupling chapters were not re-read for this page; results are from derivation, the primary papers' abstracts/author versions, and own MoM.

## Sources
1. R. J. Mailloux, *Phased Array Antenna Handbook*, 2nd ed., Artech House, 2005, ch. 2 (planar arrays, lattices, u-v space), ch. 6 "Summary of element pattern and mutual impedance effects". (textbook)
2. R. C. Hansen, *Phased Array Antennas*, 2nd ed., Wiley, 2009 — mutual coupling, scan impedance, finite-array effects, blindness. (textbook)
3. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016, ch. 6 (planar arrays) and ch. 8 (mutual impedance of dipoles). (textbook)
4. P. W. Hannan, "The element-gain paradox for a phased-array antenna," *IEEE Trans. Antennas Propag.* 12(4):423–433, 1964 — embedded element gain 4πA/λ² cosθ; N × element gain = array gain. (peer-reviewed; abstract read)
5. P.-S. Kildal, A. Vosoogh, S. Maci, "Fundamental directivity limitations of dense array antennas: a numerical study using Hannan's embedded element efficiency," *IEEE Antennas Wireless Propag. Lett.*, 2015, doi:10.1109/LAWP.2015.2473136 (author version, Chalmers CPL 230414) — e_emb = 1 − Σ|S_ij|², Hannan asymptote πd_x d_y/λ², infinite-array integral over Γ_a. (peer-reviewed)
6. E. D. Sharp, "A triangular arrangement of planar-array elements that reduces the number needed," *IRE Trans. Antennas Propag.* 9(2):126–129, 1961 — 13.4% saving. (peer-reviewed; abstract read)
7. D. M. Pozar, "The active element pattern," *IEEE Trans. Antennas Propag.* 42(8):1176–1178, 1994 — AEP predicts scan performance; relation to active reflection coefficient. (peer-reviewed; abstract read)
8. D. M. Pozar, D. H. Schaubert, "Scan blindness in infinite phased arrays of printed dipoles," *IEEE Trans. Antennas Propag.* 32(6):602–610, 1984 — blindness from Floquet-mode/surface-wave coupling, validated by waveguide simulator. (peer-reviewed; abstract read)
9. H. A. Wheeler, "Simple relations derived from a phased-array antenna made of an infinite current sheet," *IEEE Trans. Antennas Propag.* 13(4):506–514, 1965 — scan resistance ∝ secθ (E) / cosθ (H). (peer-reviewed; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content from memory of standard texts, not re-read)
10. P. W. Hannan, "Proof that a phased-array antenna can be impedance matched for all scan angles," *Radio Science* 2(3):361–369, 1967. (peer-reviewed; title/venue confirmed by search)
11. P. Delos, B. Broughton, J. Kraft, "Phased Array Antenna Patterns — Part 3," *Analog Dialogue* 54(3), 2020 — mutual coupling as an error term, edge vs centre elements. (app note)
12. `tools/verify/array_planar.py` and `tools/verify/ant_mom_wire.py` — all MoM and lattice numbers. (own verification)
