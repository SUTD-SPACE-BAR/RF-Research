---
title: Microstrip patch antennas — models, design equations, feeds, bandwidth, efficiency, circular polarization
domain: 08-antennas
slug: patch-antennas
tags: [patch, microstrip-antenna, cavity-model, transmission-line-model, hammerstad, inset-feed, probe-feed, aperture-coupled, surface-waves, circular-polarization, truncated-corner, fr-4, rogers, gnss, 2.4ghz, 5.8ghz]
prerequisites: [antenna-fundamentals.md, ../03-transmission-lines-matching/planar-lines-microstrip-stripline-cpwg.md, ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md, ../02-electromagnetics/waveguides-and-cavity-resonators.md]
related: [gnss-antennas.md, antenna-polarization-and-circular-polarization.md, small-antenna-limits.md, antenna-simulation-nec-openems.md, antennas-on-rockets.md, ../12-phased-arrays/array-factor-linear-arrays.md, ../20-projects-recipes/patch-antenna-design-walkthrough.md, ../13-pcb-rf-layout-emc/stackups-and-materials.md, slot-antennas.md, lens-and-reflectarray-antennas.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Microstrip patch antennas

## Questions this page answers
- How does a flat square of copper over a ground plane radiate?
- How do I calculate the width and length of a patch for 2.45 GHz on FR-4, or for GNSS L1 on Rogers?
- Why is my FR-4 patch's gain only ~2 dBi when the textbooks say 6–7 dBi?
- Why is patch bandwidth only 1–3 %, and how do I widen it?
- Where do I put the feed so it is 50 Ω (inset depth, probe position)?
- What are surface waves and why do thick, high-εr substrates lose efficiency?
- How do truncated-corner patches make circular polarization, and how big should the truncation be?
- What is the difference between probe, inset, aperture-coupled and proximity-coupled feeds?
- Can I make a 915 MHz or 433 MHz patch for a ground station or a rocket?
- How do I verify a patch design in openEMS before ordering boards?

## TL;DR
- A rectangular patch of length L ≈ λ_g/2 is a leaky **cavity** (open "magnetic walls" at its edges). The two edges at the ends of L act as **radiating slots**; the fields there add broadside. Directivity is 6–7 dBi on typical PCB substrates and 8–10 dBi on air/foam (verified: `tools/verify/ant_patch.py`).
- **Design equations** (TL model + Hammerstad fringing) — W = (c/2f)√(2/(εr+1)); ε_eff = (εr+1)/2 + (εr−1)/2·(1+12h/W)^(−1/2); ΔL = 0.412h(ε_eff+0.3)(W/h+0.264)/[(ε_eff−0.258)(W/h+0.8)]; L = c/(2f√ε_eff) − 2ΔL.
- **Results** for the reader's bands (TL model + Jackson–Alexopoulos CAD formulas): 2.45 GHz on FR-4 1.6 mm: **37.2 × 28.8 mm**, BW ≈ 2.6 %, efficiency ≈ 40 %, G ≈ 2 dBi; same on RO4003C 1.524 mm: **40.6 × 32.1 mm**, e ≈ 76 %, G ≈ 5.2 dBi; GNSS L1 on RO4003C: **63.1 × 50.2 mm**; 5.8 GHz on RO4350B 0.762 mm: **16.9 × 13.3 mm**; 915 MHz on FR-4: 98.8 × 77.1 mm but only ≈ 20 % efficient (−1 dBi) — use air/foam at sub-GHz.
- **Bandwidth ∝ h/(λ₀εr)·(W/L)** for thin substrates: ≈ 3 % for εr = 2.2 at h = 0.02λ₀ (Jackson; our script 2.8 %). CP axial-ratio bandwidth is about half the impedance bandwidth.
- **Efficiency**: thin substrates → conductor and dielectric loss dominate (FR-4's tanδ ≈ 0.02 is the killer); thick/high-εr substrates → surface-wave loss. For εr = 2.2 the optimum is h ≈ 0.02λ₀ [2].
- **Feed resistance** at the radiating edge is ~70–700 Ω and falls as cos²(πx₀/L) moving toward the centre; a probe or inset at the right depth gives 50 Ω.
- **Circular polarization** from a single feed needs two orthogonal modes split by Δf ≈ f₀/Q (each ±45°): our two-mode model shows AR = 0 dB exactly at split = 1/Q. Truncate corners or use a nearly-square patch fed on the diagonal; or feed two edges with a 90° hybrid for wider AR bandwidth.
- FR-4's εr tolerance (4.2–4.6) moves resonance by ±2.3 % at 2.45 GHz — larger than the patch's bandwidth. Plan to tune, or use a controlled-εr laminate.

## Intuition (no math)
Take a sheet of copper a little under half a guided wavelength long, held a small height h above a ground plane with dielectric in between. Feed it and a standing wave builds up along L: the electric field under the patch points *up* at one end and *down* at the other, with a null in the middle. At the two ends, the field "fringes" out beyond the edge. Look at these fringing fields from above: at both edges the *horizontal* part of the fringing field points the same way. So the two edges act like two slots radiating in phase, λ_g/2 apart; broadside (straight up) their fields add.

The patch is therefore mostly a **resonant cavity** that leaks a little energy through its edges. Because it stores a lot of energy relative to what it radiates (high Q), it is narrowband. Making the substrate thicker lets more field fringe out (more radiation, lower Q, more bandwidth); raising εr concentrates the field under the patch (smaller patch, less radiation, narrower band, and more energy launched sideways into the substrate as surface waves).

Where you feed it matters because the voltage between patch and ground is maximum at the radiating edges and zero in the middle, while the current is the reverse. Feeding at the edge sees a high impedance (hundreds of Ω); moving inward the impedance drops smoothly to zero at the centre. Somewhere in between it is 50 Ω.

## The math

### Level 1 — design equations (what you type into a calculator)

Symbols: f = design frequency (Hz); c = 299 792 458 m/s; εr = substrate relative permittivity; h = substrate thickness (m); W = patch width (non-resonant dimension); L = resonant length (along the feed direction for the TM₁₀ mode); λ₀ = c/f; k₀ = 2π/λ₀; η₀ = 376.73 Ω; tanδ = loss tangent; R_s = surface resistance of copper = √(πfμ₀/σ).

1. **Width** (a good radiator; not critical):
$$W=\frac{c}{2f}\sqrt{\frac{2}{\varepsilon_r+1}}$$
2. **Effective permittivity** (the patch as a wide microstrip line):
$$\varepsilon_\text{eff}=\frac{\varepsilon_r+1}{2}+\frac{\varepsilon_r-1}{2}\Big(1+\frac{12h}{W}\Big)^{-1/2}$$
3. **Fringing length extension** (Hammerstad [5]):
$$\Delta L=0.412\,h\,\frac{(\varepsilon_\text{eff}+0.3)(W/h+0.264)}{(\varepsilon_\text{eff}-0.258)(W/h+0.8)}$$
4. **Physical length**:
$$L=\frac{c}{2f\sqrt{\varepsilon_\text{eff}}}-2\Delta L$$
5. **Resonant frequency of any rectangular patch** (cavity model with effective dimensions): f_mn ≈ (c/2√ε_eff)·√[(m/L_e)² + (n/W_e)²], L_e = L + 2ΔL. Keep W < 2L so the TM₀₂ mode stays above TM₁₀; W ≈ 1.5L is typical (Jackson [2]).

Performance (Jackson & Alexopoulos 1991 CAD formulas as given by Jackson [2], [3]):
$$\frac1Q=\frac1{Q_d}+\frac1{Q_c}+\frac1{Q_{sp}}+\frac1{Q_{sw}},\quad Q_d=\frac{1}{\tan\delta},\quad Q_c=\frac{\eta_0}{2}\frac{k_0h}{R_s},\quad Q_{sp}=\frac{3}{16}\frac{\varepsilon_r}{pc_1}\frac{L}{W}\frac{1}{h/\lambda_0}$$
$$\text{BW}_{\text{VSWR}\le2}=\frac{1}{\sqrt2\,Q},\qquad e_\text{rad}=\frac{1/Q_{sp}}{1/Q},\qquad R_\text{in}(x_0)=R_\text{edge}\cos^2\!\frac{\pi x_0}{L}$$
with c₁ = 1 − 1/εr + 0.4/εr², p ≈ 1 − 0.0166(k₀W)² + … (full series in the script), Q_sw = Q_sp·e_hed/(1−e_hed), and x₀ = distance of the feed from the radiating edge along L (inset depth), in the TM₁₀ mode.

### Level 2 — the two models

**(a) Transmission-line model.** Treat the patch as a length L of wide microstrip (characteristic admittance Y₀, propagation constant β = k₀√ε_eff) terminated at each end by a slot admittance Y_s = G + jB. The slot conductance for W ≪ λ₀ is G ≈ W²/(90λ₀²) S and the susceptance B is the fringing capacitance, represented by the extension ΔL (Hammerstad's formula is a curve fit to the open-end capacitance of microstrip). Resonance occurs when the two slot admittances, transformed through the line, give a real total admittance — for a symmetric patch when β(L + 2ΔL) = π, i.e. L + 2ΔL = λ_g/2, which is design step 4. The input conductance at the edge is ~2G (both slots, ignoring mutual coupling), so the edge resistance ≈ 1/(2G) ≈ 45(λ₀/W)² Ω — a few hundred ohms for W ≈ λ₀/3. The TL model gets the resonant frequency to within ~1–2 % for thin substrates but ignores the field variation along W and the finite ground plane.

**(b) Cavity model.** Because h ≪ λ₀, the region under the patch is a thin cavity with electric walls top and bottom and approximately *magnetic* walls (tangential H ≈ 0) around the perimeter. The fields are E_z ∝ cos(mπx/L)cos(nπy/W), giving modes TM_mn at the frequencies of step 5. For TM₁₀, E_z is maximum and opposite at x = 0 and x = L and zero at the centre. By the equivalence principle, the perimeter fields are replaced by magnetic surface currents M = −2n̂ × E (the factor 2 from the image in the ground plane). On the two radiating edges (x = 0, L) M points along y and is uniform in y and *in phase*; on the non-radiating edges M varies as cos(πx/L) and is antisymmetric, so their far fields cancel in the principal planes. The far field is then that of two y-directed magnetic line sources of length W separated by L_e:
$$U(\theta,\phi)\propto\big[\cos^2\phi+\cos^2\theta\sin^2\phi\big]\;\mathrm{sinc}^2\!\Big(\frac{k_0W}{2}\sin\theta\sin\phi\Big)\;\cos^2\!\Big(\frac{k_0L_e}{2}\sin\theta\cos\phi\Big)$$
over the upper hemisphere (φ = 0 is the E-plane). Integrating numerically gives D = 6.0–6.4 dBi for PCB substrates and 9.2–9.3 dBi for air (script). Jackson's CAD formula D ≈ 3/(pc₁) (thin substrates) gives 0.2–0.4 dB more for PCB cases and ~0.8 dB more for air; the difference comes from how the substrate and the magnetic-current model handle the horizon. Measured patches on finite ground planes typically come in at 5–7 dBi on FR-4/Rogers and 8–9.5 dBi on air.

**(c) Why the cos² feed law.** In the cavity model the modal voltage across the substrate at the feed location scales as cos(πx₀/L) (TM₁₀ field), and the radiated power is fixed by the mode amplitude. The input resistance R = |V|²/(2P) therefore scales as cos²(πx₀/L): R(x₀) = R_edge cos²(πx₀/L). For a probe feed this is accurate; for an inset microstrip feed the notches perturb the fields and the actual 50 Ω inset depth differs somewhat from the cos² prediction — use it as a starting point and simulate.

**(d) Q, bandwidth and efficiency.** Each loss mechanism contributes a Q: dielectric Q_d = 1/tanδ; conductor Q_c (depends on h/δ_skin); space-wave radiation Q_sp (∝ εr/(h/λ₀)); surface-wave Q_sw. Radiation efficiency is the fraction of the total 1/Q due to space-wave radiation. Two useful consequences:
- For FR-4 (tanδ ≈ 0.02 → Q_d = 50) and a 1.6 mm board at 2.45 GHz, Q_sp ≈ 68: dielectric loss absorbs nearly 60 % of the power → e_rad ≈ 40 % (script). At 915 MHz the same board is electrically thinner (Q_sp ≈ 200) and e_rad falls to ≈ 20 %.
- For Rogers RO4003C (tanδ 0.0027, Q_d ≈ 370), the same patch is ≈ 76 % efficient (the rest mostly conductor and surface-wave loss).

**(e) Surface waves.** A grounded dielectric slab guides a TM₀ surface wave with *no* cutoff and a TE₁ wave above f_c = c/[4h√(εr−1)] (Balanis ch. 14 [1]; Pozar [4]). Power launched into these waves travels along the board, diffracts off its edges, raises back-lobe and cross-polarization, and is lost to the intended beam. The horizontal-dipole surface-wave efficiency e_hed = 1/[1 + (3/4)π(k₀h)(1/c₁)(1−1/εr)³] captures the trend: for εr = 10.8 at h = 0.02λ₀ about 20 % of the power goes into surface waves (Jackson's plot; our script: e_sw ≈ 80 %), for εr = 2.2 only ≈ 7 %.

**(f) Circular polarization from one feed.** Two degenerate modes (TM₁₀ along x, TM₀₁ along y) radiate orthogonal linear polarizations. If a single feed excites both equally and they are 90° apart in phase, the radiation is CP. A single feed gives equal amplitudes when fed on the diagonal; the 90° comes from detuning the modes: model each as a parallel RLC, V_i = 1/[1 + jQ(f/f_i − f_i/f)]. At the mean frequency f₀ each mode must be ±45°, which requires Q(f/f₁ − f₁/f) = +1 and Q(f/f₂ − f₂/f) = −1, i.e. f₂ − f₁ ≈ f₀/Q. Our script confirms: split = 1.0/Q → AR = 0.00 dB at f₀; split = 0.5/Q or 1.5/Q → the minimum AR is only 6.0 / 3.5 dB; and the 3-dB AR bandwidth (1.15 % for Q = 30) is about half the VSWR-2 impedance bandwidth of one mode (2.36 %). The split is produced by a nearly-square patch (L₂/L₁ ≈ 1 + 1/Q), by truncating two opposite corners (the handbook design rule for the truncated area is ΔS/S ≈ 1/(2Q₀) [6]), or by a diagonal slot. The sense (RHCP/LHCP) is set by which diagonal carries the perturbation relative to the feed.

### Level 3 — general forms and limits
- **Thick substrates (h > ~0.05λ₀)**: the probe inductance X_p ≈ (η₀/2π)k₀h[−γ + ln(2/(√εr k₀a))] (γ = 0.5772, a = probe radius; Jackson [2]) becomes large and prevents a match; use capacitive-coupled probes, L-probes, or aperture/proximity feeds. The TL/cavity models lose accuracy (TM₀₁ and higher modes, and radiation from the probe itself) — use full-wave simulation.
- **Finite ground plane**: edge diffraction mostly affects the E-plane (ripple, back radiation ~−10 to −20 dB). A ground extending ≥ λ₀/4 beyond each edge keeps the main beam close to the infinite-ground result; GNSS ceramic patches are tuned for a specific ground size (u-blox: 50–70 mm square for L1; AR degraded to ~10 dB on 100 mm in one example [7]) — see [gnss-antennas](gnss-antennas.md).
- **Bandwidth ceiling**: a patch is an electrically small-ish resonator in height; its Q exceeds the Chu–McLean bound for its enclosing sphere by a large factor. Wideband variants (stacked patches, U-slot, aperture-coupled on foam) reach 10–30 %, and 100 % has been reported with special feeds and stacks (Jackson [2]).
- **Arrays**: patch elements combine easily in corporate or series feeds; see [array factor](../12-phased-arrays/array-factor-linear-arrays.md) and [planar arrays and element coupling](../12-phased-arrays/planar-arrays-element-pattern-coupling.md).

## Feed methods

| Feed | How | Pros | Cons | Typical use |
|---|---|---|---|---|
| Inset microstrip | line enters a notch to depth x₀ | single layer, easy to etch | notch perturbs pattern (cross-pol); line radiates; BW limited | 2.4/5.8 GHz single patches and series arrays |
| Edge-fed + λ/4 transformer | 50 Ω → λ_g/4 of √(50R_edge) → edge | predictable | extra length; narrow; high-Z line may be very thin | classic student designs |
| Coax probe | centre pin through ground and substrate at x₀ | no feed radiation; feed behind ground | probe inductance limits h; drilling/soldering | GNSS ceramic patches (pin at ~1/3 from centre) |
| Aperture-coupled | feed line on a lower layer couples through a slot in the ground | feed shielded; thick foam patch possible; wide BW | 3+ layers; back radiation from slot | wideband and array tiles |
| Proximity-coupled | open-ended line under the patch on a middle layer | wide BW, low spurious radiation | 2 substrates, alignment | wideband single patches |
| Dual-feed + 90° hybrid | two orthogonal edges fed 0°/90° | wide AR bandwidth, pure CP | hybrid loss and size | high-quality CP (GNSS reference, telemetry ground antennas) |

## Design equations & rules of thumb

| Item | Rule | Notes |
|---|---|---|
| Resonant length | L ≈ 0.49 λ₀/√εr (thin substrates) | exact via steps 2–4 |
| Width | W ≈ 1.2–1.5 L | W < 2L to avoid TM₀₂ |
| Bandwidth (VSWR 2) | ≈ 3.77·(p c₁/εr)(h/λ₀)(W/L) (lossless, thin; p ≈ 0.9, c₁ = 1 − 1/εr + 0.4/εr²) | ≈ 3 % at εr 2.2, h 0.02λ₀, W = 1.5L |
| Efficiency optimum | h/λ₀ ≈ 0.02 for εr ≈ 2.2 | Jackson [2] |
| Probe limit | h ≲ 0.05λ₀ | above: inductance hard to cancel |
| TE₁ surface-wave cutoff | f_c = c/[4h√(εr−1)] | 1.6 mm FR-4: 25 GHz |
| Edge resistance | 70–700 Ω, ∝ εr·(L/W)² approximately | higher εr, narrower W → higher |
| 50 Ω feed point | R_edge cos²(πx₀/L) = 50 | probe/inset depth x₀ from edge |
| Ground plane | ≥ patch + 2×(λ₀/4) … or as specified for ceramic GNSS patches | smaller → back lobe, AR change, detuning |
| CP mode split | Δf/f₀ ≈ 1/Q | AR bandwidth ≈ ½ impedance BW |
| εr sensitivity | Δf/f ≈ −½ Δεr/εr | FR-4 4.2–4.6 → ±2.3 % |

## Worked examples

All numbers from `python3 tools/verify/ant_patch.py` (TL model + Jackson CAD; copper σ = 5.8×10⁷ S/m, smooth).

| Case | W (mm) | L (mm) | ε_eff | h/λ₀ | BW (VSWR 2) | e_rad | D (dBi, two-slot) | G (dBi) | R_edge (Ω) | 50 Ω inset x₀ (mm) | 50 Ω line (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L1 1575.42, FR-4 (4.4, 1.6 mm, tanδ 0.02) | 57.90 | 45.09 | 4.17 | 0.0084 | 2.2 % | 30 % | 6.1 | 0.9 | 101 | 11.3 | 3.06 |
| L1 1575.42, RO4003C (3.55, 1.524 mm) | 63.08 | 50.16 | 3.40 | 0.0080 | 1.0 % | 70 % | 6.3 | 4.8 | 212 | 17.0 | 3.41 |
| L1 1575.42, ceramic εr 20, 4 mm | 29.36 | 20.34 | 16.4 | 0.021 | 0.75 % | 71 % | 5.1 | 3.6 | 663 | 8.4 | — |
| 2.45 GHz, FR-4 1.6 mm | 37.23 | 28.81 | 4.08 | 0.013 | 2.6 % | 40 % | 6.1 | 2.1 | 131 | 8.3 | 3.06 |
| 2.45 GHz, RO4003C 1.524 mm | 40.56 | 32.06 | 3.33 | 0.0125 | 1.5 % | 76 % | 6.4 | 5.2 | 228 | 11.1 | 3.41 |
| 5.8 GHz, FR-4 (4.3) 1.6 mm | 15.88 | 11.88 | 3.76 | 0.031 | 4.7 % | 55 % | 6.2 | 3.6 | 166 | 3.7 | 3.11 |
| 5.8 GHz, RO4350B (3.66) 0.762 mm | 16.93 | 13.29 | 3.40 | 0.015 | 1.8 % | 73 % | 6.3 | 5.0 | 220 | 4.5 | 1.67 |
| 915 MHz, FR-4 (4.5) 1.6 mm | 98.79 | 77.05 | 4.35 | 0.0049 | 1.9 % | 20 % | 6.0 | −1.0 | 68 | 13.2 | 3.01 |
| 915 MHz, air/foam 6 mm | 161.8 | 151.9 | 1.05 | 0.018 | 2.1 % | 97 % | 9.2 | 9.1 | 272 | — (probe) | — |
| 433 MHz, air 10 mm | 346 | 332 | 1.00 | 0.014 | 1.6 % | 99 % | 9.3 | 9.3 | 286 | — (probe) | — |

**Example 1 — 2.45 GHz on FR-4, step by step.** εr = 4.4, h = 1.6 mm, f = 2.45 GHz.
1. W = (0.29979/(2×2.45×10⁹))·√(2/5.4) = 61.18 mm × 0.6086 = **37.23 mm**.
2. ε_eff = 2.7 + 1.7·(1 + 12×1.6/37.23)^(−1/2) = 2.7 + 1.7 × 0.8123 = **4.081**.
3. W/h = 23.27; ΔL = 0.412 × 1.6 × (4.381 × 23.53)/(3.823 × 24.07) = 0.659 × 1.1203 = **0.739 mm**.
4. L = c/(2f√4.081) − 2 × 0.739 = 30.29 − 1.48 = **28.81 mm**.
5. Q budget (script): Q_d = 50, Q_c ≈ 1200, Q_sp ≈ 68, Q_sw ≈ 605 → Q ≈ 27 → BW ≈ 1/(√2·27) = **2.6 %** (≈ 64 MHz — covers 2400–2483.5 MHz only if centred and not detuned), e_rad = 27/68 ≈ **40 %**, so G ≈ 6.1 dBi + 10 log 0.40 ≈ **2 dBi**.
6. Feed: R_edge ≈ 131 Ω; inset depth x₀ = (L/π)·acos(√(50/131)) = **8.3 mm**; 50 Ω microstrip ≈ 3.06 mm wide (εr 4.4, h = 1.6 mm, bare model; on JLC's 2-layer JLC0216A template, 1.43 mm core, εr 4.5, the calculator gives 2.69 mm masked — order that, [canonical width table](../13-pcb-rf-layout-emc/stackups-and-materials.md#canonical-50-ω-width-table), and note that the patch dimensions also shift with the real core thickness); notch gap typically ≈ 0.5–1 mm each side (simulate).
7. Tolerance: εr = 4.2 or 4.6 moves resonance to 2506 or 2398 MHz (±2.3 %) — as large as the whole bandwidth. Measure the laminate or order a controlled-Dk board.

**Example 2 — GNSS L1 on a ceramic puck vs FR-4.** A ceramic patch (εr ≈ 20, h = 4 mm) at 1575.42 MHz has L ≈ 20 mm, fits a 25 × 25 mm tile, but its bandwidth (≈ 0.75 %, ~12 MHz) is tight and any detuning by the enclosure or ground size moves it off L1 — which is why vendors sell pre-tuned variants for specific ground planes and u-blox warns about near-field loading [7]. The FR-4 version (57.9 × 45.1 mm) is wider-band but only ≈ 30 % efficient (≈ 1 dBi). For a single-feed RHCP GNSS patch (BW 0.75 % → Q = 1/(√2·0.0075) ≈ 94 for the ceramic case), the modes must be split by Δf ≈ f₀/Q ≈ 17 MHz, i.e. L₂/L₁ ≈ 1.011, and the AR < 3 dB bandwidth is only ≈ 0.37 % ≈ 6 MHz — enough for GPS L1 C/A (±1 MHz) but tight for Galileo E1/BeiDou B1 (±2–12 MHz, see [gnss-antennas](gnss-antennas.md)).

**Example 3 — A 915 MHz ground-station patch on air.** Two 1.6 mm FR-4 (or aluminium) sheets 6 mm apart with nylon spacers: patch 162 × 152 mm, D ≈ 9.2 dBi, e ≈ 97 %, BW ≈ 2.1 % (19 MHz) — so the 902–928 MHz band (2.8 %) is *not* fully covered; increase the gap to ~10 mm (h/λ₀ ≈ 0.03, BW ≈ 3.5 %) and probe-feed it at the 50 Ω point (a few cm in from the edge; the probe inductance at h = 10 mm is modest at 915 MHz). Compared with a 3-element Yagi (≈ 9 dBi, see [yagi](yagi-uda-and-log-periodic.md)) it is flatter and more robust but larger in area. For rocket tracking, make it CP (dual-feed with a 90° hybrid) to avoid roll fades ([antennas-on-rockets](antennas-on-rockets.md)).

**Example 4 — 5.8 GHz video/telemetry patch on RO4350B.** 16.93 × 13.29 mm, 0.762 mm board, BW 1.8 % (≈ 104 MHz) — covers only part of the 5725–5875 MHz band; move to 1.524 mm (BW ≈ 3.5 %) if the whole band is needed.

**Example 5 — Why nobody etches a 433 MHz patch.** On air it would be 35 × 33 cm; on FR-4 about 16 × 16 cm and ≈ 10 % efficient. At 433 MHz a Yagi, a crossed-dipole turnstile or a helix gives more gain per kilogram.

## Practical notes
- **FR-4 is a poor patch substrate above ~1 GHz** because of tanδ ≈ 0.015–0.025 and loosely controlled εr (≈ 4.2–4.7 depending on glass/resin ratio and frequency). JLCPCB and similar fabs publish εr for their stack-ups; use their numbers for the thin prepreg/core actually used ([stack-ups](../13-pcb-rf-layout-emc/stackups-and-materials.md), [JLCPCB RF manufacturing](../13-pcb-rf-layout-emc/jlcpcb-rf-manufacturing.md)).
- **Rogers RO4003C/RO4350B** (εr 3.38/3.48 process, 3.55/3.66 design Dk, tanδ ≈ 0.0027/0.0037) are the common low-cost controlled laminates; many fabs offer them as hybrid stack-ups.
- **Copper roughness and plating** increase R_s (and lower Q_c); ENIG nickel adds loss at >5 GHz. Solder mask over the patch lowers the resonance slightly (≈ 0.5–1 %) — keep it off the patch or model it.
- **Tuning**: build 1–2 % large and trim the radiating edges (shortening L raises f). Copper tape can lengthen. For probe-fed patches, moving the probe changes R but hardly f.
- **Ground plane and enclosure**: a radome or rocket skin within ~λ/10 of the patch detunes it downward; model the radome.
- **Connector launch**: an SMA end-launch on a thin board needs its own matching; a poor launch can look like a patch mismatch.
- **Cross-polarization**: inset notches and feed-line radiation raise cross-pol; aperture/proximity feeds or probe feeds give cleaner patterns.
- **Suppressing surface waves with an EBG (mushroom) ground plane**, and how much to expect from it: [03 periodic structures and EBG](../03-transmission-lines-matching/periodic-structures-ebg.md#level-3--ebgmushroom-surfaces-crlh-lines-and-where-the-models-break).

## Common mistakes & misconceptions
- **"Patch antennas are 6–9 dBi."** That is directivity. On FR-4 at 915 MHz–2.45 GHz the *gain* is often −1 to +3 dBi because of dielectric loss.
- **"Just scale the 2.4 GHz patch to 915 MHz."** Dimensions scale, but h/λ₀ does not unless you also scale the thickness, so bandwidth and efficiency collapse on the same board.
- **"The edge impedance is always ~200 Ω."** It ranges from < 100 Ω (thin lossy boards, where loss lowers the resonant resistance, or very wide patches) to > 600 Ω (high-εr ceramic); compute it.
- **"W sets the frequency."** L does (for TM₁₀). W sets edge resistance, bandwidth and whether TM₀₂ interferes.
- **"Thicker is always better."** Up to a point: the probe inductance and surface waves grow with h; beyond ~0.05λ₀ change the feed type.
- **"Any square patch with a diagonal feed is CP."** Without the correct 1/Q mode split it is elliptical or linear. The split must be designed against the *loaded* Q.
- **"The patch radiates from its whole surface."** Radiation comes from the fringing fields at the two radiating edges (and, for higher-order considerations, the perimeter currents); the centre carries current but little fringing field.
- **Forum-observed** (r/rfelectronics, EE Stack Exchange — anecdotal): calculator outputs used without a full-wave check, then the board resonates 50–100 MHz low because the calculator assumed εr = 4.4 while the fab's prepreg was ≈ 4.1–4.2 at 2.4 GHz, or because solder mask and connector launch were ignored.

## How to simulate / verify
- **Quick numbers**: `python3 tools/verify/ant_patch.py` prints the table above, a Q budget, εr sensitivity, the Jackson BW/efficiency sweep vs h/λ₀ (e.g. εr 2.2: 1.3/2.8/6.0/9.8 % at h/λ₀ = 0.01/0.02/0.04/0.06), and the CP two-mode AR check. Edit `cases` for your substrate.
- **openEMS (recommended free full-wave tool)** — follow the official "Simple Patch Antenna" tutorial [8]:
  1. Build patch, substrate (finite, same size as the board) and ground; define εr and a conductivity/κ for the loss tangent at the design frequency.
  2. Excite with a lumped port (probe) or an MSL port on the feed line; 50 Ω reference.
  3. Mesh: ≤ λ/20 in the dielectric at the highest frequency, thirds-rule refinement at the patch edges, at least 3–4 cells across h.
  4. Boundaries: MUR or PML ≥ λ/4 from the structure at the lowest frequency; add an NF2FF box inside the boundary.
  5. Run a Gaussian pulse spanning ±20 % of f₀; post-process S11, Z_in, and at resonance the far field: directivity and radiated power; e_rad = P_rad/P_accepted.
  6. Check against the TL model: resonance within ~2 %; if not, look for εr mistakes, mesh too coarse at edges, or port de-embedding errors.
- **NEC** cannot model the dielectric substrate; don't use it for patches ([antenna-simulation-nec-openems](antenna-simulation-nec-openems.md)).
- **Bench**: NanoVNA S11 (resonance, bandwidth); for gain/efficiency and CP axial ratio, see [antenna measurement](antenna-measurement.md) (rotating linear source for AR).

## Open questions / gaps
- The truncated-corner rule ΔS/S = 1/(2Q₀) is quoted from the microstrip handbook literature via secondary citation; derive and confirm with openEMS before relying on it (our two-mode model confirms only the frequency-split requirement).
- An openEMS run of the 2.45 GHz FR-4 inset patch (to validate inset depth vs the cos² law) is not yet done — W3-C2 (16-simulation-tools) could add it as a worked openEMS example.
- FR-4 εr/tanδ at 1–6 GHz for specific JLCPCB stack-ups should come from domain 13/18.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., Wiley, 2016 — ch. 14 (microstrip antennas: TL model W/ε_eff/ΔL/L design equations, cavity model, fields, directivity, feeds, surface waves, CP). (textbook)
2. D. R. Jackson, "Introduction to Microstrip Antennas," Univ. of Houston ECE 5318/6345 lecture notes — CAD formulas (Q_d, Q_c, Q_sp, Q_sw, e_hed, p, c₁, BW = 1/(√2Q), R_edge, cos² feed law, probe reactance, D ≈ 3/(pc₁)); BW ≈ 3 % at h/λ₀ = 0.02 and εr = 2.2; ~10 % on thick foam; efficiency optimum h/λ₀ ≈ 0.02; W = 1.5L typical, W < 2L. https://courses.egr.uh.edu/ECE/ECE5318/Introduction%20to%20Microstrip%20Antennas.pdf (lecture notes)
3. D. R. Jackson and N. G. Alexopoulos, "Simple approximate formulas for input resistance, bandwidth, and efficiency of a resonant rectangular patch," *IEEE Trans. Antennas Propag.*, vol. 39, no. 3, pp. 407–410, 1991; also D. R. Jackson, "Microstrip Antennas," ch. 7 in J. L. Volakis (ed.), *Antenna Engineering Handbook*, 5th ed., McGraw-Hill, 2019. (peer-reviewed / handbook)
4. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley, 2012 — microstrip synthesis (W/h for 50 Ω), grounded dielectric slab surface waves; D. M. Pozar, "Rigorous closed-form expressions for the surface-wave loss of printed antennas," *Electron. Lett.* 26, pp. 954–956, 1990. (textbook / peer-reviewed)
5. E. O. Hammerstad, "Equations for microstrip circuit design," *Proc. 5th European Microwave Conf.*, pp. 268–272, 1975 — open-end length extension ΔL. (peer-reviewed; formula as reproduced in Balanis eq. 14-2)
6. R. Garg, P. Bhartia, I. Bahl, A. Ittipiboon, *Microstrip Antenna Design Handbook*, Artech House, 2001 — singly-fed CP designs (nearly-square, truncated corners, ΔS/S = 1/(2Q₀)), stacked and aperture-coupled patches; J. R. James and P. S. Hall (eds.), *Handbook of Microstrip Antennas*, IEE/Peregrinus, 1989. (handbooks; CP rule cited secondarily)
7. u-blox, *GNSS antennas — RF design considerations*, UBX-15030289 R03, 2019 — ceramic patch sizes, ground-plane dependence of gain, AR and centre frequency. https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf (app note)
8. openEMS, "Tutorial: Simple Patch Antenna" (Python and MATLAB) and NF2FF documentation. https://docs.openems.de/python/openEMS/Tutorials/Simple_Patch_Antenna.html (tool documentation)
9. P. C. Ribeiro Filho, A. F. Tinoco-S., D. C. Nascimento, J. C. da S. Lacava, "A Telemetry Antenna Design for a Sounding Rocket Competition," *IEEE Antennas Propag. Mag.* 59, 2017 — truncated-corner CP patch ground-station antenna and wraparound array for a student rocket. (peer-reviewed; abstract level)
10. This repository: `tools/verify/ant_patch.py` (TL model, Jackson CAD, two-slot directivity, CP two-mode model). (verification)
