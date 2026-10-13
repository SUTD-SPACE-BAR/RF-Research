---
title: Yagi-Uda and log-periodic dipole antennas — how parasitic arrays work, DL6WU design, 433/915 MHz ground-station Yagis, LPDA design
domain: 08-antennas
slug: yagi-uda-and-log-periodic
tags: [yagi, yagi-uda, parasitic-array, dl6wu, reflector, director, boom-correction, stacking, crossed-yagi, lpda, log-periodic, carrel, ground-station, corner-reflector, two-element-yagi, front-to-side, front-to-rear]
prerequisites: [antenna-fundamentals.md, dipoles-and-monopoles.md, ../12-phased-arrays/array-factor-linear-arrays.md]
related: [../12-phased-arrays/stacking-and-arraying-yagis.md, antenna-matching-and-baluns.md, antenna-polarization-and-circular-polarization.md, antennas-on-rockets.md, antenna-simulation-nec-openems.md, antenna-measurement.md, ../15-lora-ism-radios/ground-station-design.md, ../20-projects-recipes/ground-station-tracking-yagi.md, multiband-and-wideband-antennas.md, antenna-identification-guide.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Yagi-Uda and log-periodic dipole antennas

## Questions this page answers
- How can un-driven metal rods (directors, reflector) make an antenna directional?
- Why is the reflector longer and the directors shorter than the driven element?
- How much gain do I get per metre of boom, and why does it grow so slowly?
- How do I design a 433 MHz or 915 MHz Yagi for a rocket ground station (DL6WU method)?
- Does a metal boom change the element lengths? By how much?
- Why is a 3-element Yagi's feed impedance so low and how do I match it?
- How accurately must I cut the elements?
- How do I stack two Yagis, or make a circularly polarized crossed Yagi?
- What is a log-periodic dipole array (LPDA), and how do I choose τ and σ?
- Should I use a Yagi or an LPDA for a ground station?
- How does a corner reflector work, and is it a better ground-station antenna than a Yagi?
- In a 2-element Yagi, is the parasitic element better as a reflector or a director?
- What are front-to-back, front-to-rear and front-to-side ratios?
- Which stacking distance is right: 51/HPBW or λ/(2 sin(B/2))?

## TL;DR
- A Yagi is a dipole plus parasitic dipoles coupled by mutual impedance. Each parasitic element's current is I₂ = −(Z₂₁/Z₂₂)I₁: a **longer** (inductive) element's current lags and it acts as a **reflector**; a **shorter** (capacitive) element leads and acts as a **director**. Long Yagis are best understood as a slow-wave (surface-wave) structure along the director chain.
- **Gain grows only logarithmically with boom length**: DL6WU's estimate G ≈ 9.2 + 3.39 ln(boom/λ) dBd (2.2–39λ). Our MoM of DL6WU designs: 433 MHz **11 el, 1.72 m → 14.2 dBi**; **15 el, 2.78 m → 15.9 dBi**; 915 MHz **11 el, 0.82 m → 14.3 dBi**; **16 el, 1.45 m → 16.3 dBi** (≈0.1–0.2 dB below the DL6WU estimate). Doubling the boom adds ≈ 2.3 dB, not 3 dB.
- A good **3-element** Yagi gives ≈ 9 dBi and F/B ≈ 15 dB on a 0.35λ boom (MoM optimum: 9.15 dBi, 242 mm boom at 433 MHz) but its feed impedance is only ≈ 11 Ω with a plain dipole — use a folded dipole (≈ ×4 → ~45 Ω), hairpin or gamma match. If instead it must be **fed directly from 50 Ω** (VSWR ≤ 1.5 and F/B ≥ 15 dB across 433.05–434.79 MHz), the NEC optimum is **≈ 8.5 dBi** (8.55 dBi, Z 34 Ω; [NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md)) — so budget **≈ 8.5 dBi for a buildable 3-element Yagi**, ≈ 9 dBi only with a separate low-loss match.
- **DL6WU spacings** (λ, reflector at 0): driven element 0.200, then 0.075, 0.180, 0.215, 0.250, 0.280, 0.300, 0.315, 0.330, 0.345, 0.360, 0.375, 0.390, 0.400, then 0.400 constant. Directors taper from ≈0.43λ to ≈0.38λ; the design is broadband (2:1 SWR ≈ ±5 %) and forgiving.
- **Tolerances**: DL6WU specifies element lengths to ±0.003λ (±2.1 mm at 433 MHz, ±1.0 mm at 915 MHz). Through-boom bonded mounting needs a boom correction (DL6WU fit, a fraction of the boom diameter added to each element; half for insulated through-boom; none for elements ≥ one boom radius above a non-conducting or clear boom).
- **LPDA** (Carrel): elements scale by τ, spacing σ = d/(2L); cot α = 4σ/(1−τ); σ_opt ≈ 0.243τ − 0.051; active-region bandwidth B_ar = 1.1 + 7.7(1−τ)²cot α; N = 1 + ln(B·B_ar)/ln(1/τ). Gain 6.5–10 dBi, nearly constant over a decade — but less gain than a Yagi of the same boom length.
- **Corner reflector** (90°, dipole S = 0.5λ from the apex, rod screen with 2S sides): NEC **9.7 dBi, F/B 25 dB, R ≈ 133 Ω**, VSWR ≤ 1.33 across ±6 %. Image theory (infinite sheets) gives 11.8 dBi; a 1.5λ × 1λ screen reaches 11.1 dBi. It is a broadband, forgiving alternative to a 3–5-element Yagi.
- **2-element Yagi**: the director type gives slightly more gain (7.4 vs 7.2 dBi at 0.05λ), but both feed impedances are only 4–14 Ω at the close spacings where gain peaks. Practical builds use 0.1–0.15λ (7.0–7.3 dBi, 14–31 Ω, F/B only 5–7 dB).
- **F/S** (front-to-side) in the element plane is infinite (the dipole null). In the other plane it is 18 dB for the 3-element and 21 dB for the 11-element Yagi (NEC). F/R equals F/B for these designs.
- **Stacking distance**: the DL6WU/G3SEK rule D = λ/(2 sin(B/2)) gives slightly more gain (+2.9–3.0 dB for two 11-element Yagis). The older 51/HPBW rule gives lower stacking lobes (+2.7 dB, −15 dB lobes). Both are within 0.4 dB of the maximum ([stacking](../12-phased-arrays/stacking-and-arraying-yagis.md)).
- For tracking a rolling rocket, use **CP on the ground** (crossed Yagi with a 90° phasing line, or an axial helix) to avoid polarization fades — see [antennas-on-rockets](antennas-on-rockets.md).

## Intuition (no math)
Put a second dipole near a driven dipole. The driven dipole's field induces a current in the second one, which re-radiates. Whether that re-radiation adds forward or backward depends on its phase, which depends on (1) the spacing (the wave takes time to travel between them) and (2) whether the parasitic element is tuned above or below resonance. A slightly long element (inductive) carries a current that lags; placed ~0.15–0.25λ behind the driven element, its re-radiation cancels the backward wave and reinforces the forward one — a **reflector**. A slightly short element (capacitive) leads; placed in front, it pulls the wave forward — a **director**.

With many directors, the row of short rods behaves like a **waveguide for a slow wave**: the wave clings to the director chain (like a surface wave on a dielectric rod) and travels along it slightly slower than light, then launches off the end. The longer the chain, the more coherent the end-fire beam — but each extra director contributes a little less, because the wave's phase velocity and the chain's "capture" of the wave are only approximately right. Hence logarithmic gain growth.

An **LPDA** is a different idea: all dipoles are driven through a criss-crossed feeder, and at any frequency only the few elements near λ/2 long (the "active region") radiate strongly, with the shorter elements in front acting like directors and the longer ones behind hardly excited. Change frequency and the active region slides along the array, so the pattern and impedance are nearly frequency-independent.

## The math

### Level 1 — two-element array and what drives design

For a driven element 1 and a shorted (parasitic) element 2:
$$V_1 = Z_{11}I_1 + Z_{12}I_2,\qquad 0 = Z_{21}I_1 + Z_{22}I_2\;\Rightarrow\; \frac{I_2}{I_1}=-\frac{Z_{21}}{Z_{22}},\qquad Z_\text{in}=Z_{11}-\frac{Z_{12}^2}{Z_{22}} .$$
Z₂₂ = R₂₂ + jX₂₂: a longer element has X₂₂ > 0 (inductive), a shorter one X₂₂ < 0. The far field is that of two sources with this complex current ratio separated by d; with I₂/I₁ = |r|e^{jψ}, the endfire field is ∝ |1 + |r|e^{j(ψ ± kd)}|. Choose ψ so that the sum peaks toward the director side and cancels toward the reflector side.

The feed impedance drops because the parasitic currents are strongly coupled at close spacing (Z₁₂ ~ 40–70 Ω at 0.1–0.2λ): 3-element Yagis optimised for gain typically present 10–25 Ω.

### Level 2 — mutual impedance, induced EMF and MoM

The induced-EMF mutual impedance of two parallel side-by-side λ/2 dipoles at spacing d (sinusoidal currents, referred to current maxima; Balanis ch. 8 [1]):
$$R_{21}=\frac{\eta_0}{4\pi}\big[2\,\mathrm{Ci}(u_0)-\mathrm{Ci}(u_1)-\mathrm{Ci}(u_2)\big],\quad X_{21}=-\frac{\eta_0}{4\pi}\big[2\,\mathrm{Si}(u_0)-\mathrm{Si}(u_1)-\mathrm{Si}(u_2)\big],$$
u₀ = kd, u₁ = k(√(d²+l²)+l), u₂ = k(√(d²+l²)−l). Values and our thin-wire MoM two-port result (`tools/verify/ant_yagi.py`):

| d/λ | Induced EMF Z₂₁ (Ω) | MoM Z₂₁ (Ω, a = 10⁻⁴λ, exact λ/2) |
|---|---|---|
| 0.10 | 67.3 + j7.5 | 74.7 + j2.9 |
| 0.25 | 40.8 − j28.3 | 41.7 − j34.6 |
| 0.50 | −12.5 − j29.9 | −16.7 − j31.2 |
| 1.00 | 4.0 + j17.7 | 6.2 + j18.9 |

They agree in trend and to within a few ohms; the differences come from the sinusoidal-current assumption and from the two-port (gap) definition. For design, trust the full MoM (NEC or our script), not the induced-EMF formulas.

**Why gain grows logarithmically.** An end-fire line source of length L with the Hansen–Woodyard phase velocity reaches D ≈ 7.28 L/λ (vs 4L/λ for ordinary end-fire; see [array factor](../12-phased-arrays/array-factor-linear-arrays.md)). A Yagi does not reach this because the director currents decay along the boom and the phase velocity is set by the director lengths — DL6WU's empirical optimisation of tapering lengths and growing spacings is a way to keep the slow wave bound over long booms. Empirically the result is G(dBd) ≈ 9.2 + 3.39 ln(B/λ) (DL6WU [3]), i.e. about +2.35 dB per doubling. Our MoM results sit 0.1–0.25 dB below this curve; Cebik's NEC models of DL6WU 432 MHz designs (4 mm elements) show 14.7 dBi at 2.85λ (12 el), 17.2 dBi at 5.6λ (19 el) and 18.6 dBi at 8.4λ (26 el) [4], also slightly below the formula (formula: 15.0, 17.2, 18.6 dBi).

### Level 3 — the DL6WU algorithm (as implemented in the G3SEK/KY4Z/W6NBI program [3])
All lengths in wavelengths, d = element diameter/λ (0.001–0.02), BD = boom diameter/λ (< 0.06).
1. **Spacings**: reflector at 0, driven element at 0.200; then add directors using the spacing sequence 0.075, 0.180, 0.215, 0.250, 0.280, 0.300, 0.315, 0.330, 0.345, 0.360, 0.375, 0.390, 0.400, 0.400 … until the boom length is used.
2. **Director n length**: l_n = (K₁ − K₂ ln n)(1 − K₃e^{−K₄n}), with (K₁, K₂, K₃, K₄) interpolated in d from DL6WU's table (e.g. d = 0.005: 0.4538, 0.02117, 0.0951, 1.007; d = 0.01: 0.4421, 0.02396, 0.1027, 1.038).
3. **Reflector**: from a length–reactance relation targeting X = +20 Ω: l_R = ½[(X − 40)/(186.88 ln(2/d) − 320) + 1].
4. **Driven element** (folded dipole): l_DE = 1.02 × ½[0.4777 − 1.0522d + 0.43363 d^(−0.014891)].
5. **Boom correction** (added to every parasitic element): BC = [733·BD(0.055 − BD) − 504·BD(0.03 − BD)]·BD for elements bonded through a metal boom; half that for insulated through-boom elements; zero for non-metal booms or elements mounted clear of the boom.
6. **Performance estimates**: G = 9.2 + 3.39 ln(boom) dBd; horizontal (E-plane) beamwidth ≈ 30 − 3.14(G_dBd − 14) degrees. For the stacking distance, G3SEK gives DL6WU's D = λ/(2 sin(B/2)), which puts the pair's array-factor null on the single Yagi's −3 dB angle. This page previously quoted ≈ 51/HPBW λ, a rule of untraced origin that is 11–14 % closer. NEC for two 11-element 433 MHz Yagis gives +2.94/+3.02 dB (E/H) with λ/(2 sin(B/2)) and lobes at −11 to −12 dB. With 51/HPBW it gives +2.72/+2.69 dB with lobes at −15/−14 dB. Both are within 0.4 dB of the maximum (+3.1 dB at 1.6–2.1λ) ([stacking](../12-phased-arrays/stacking-and-arraying-yagis.md#level-2--derivations)). Use λ/(2 sin(B/2)) for gain, or 51/HPBW if the stacking lobes matter more.
Our Python port is `dl6wu_design()` in `tools/verify/ant_yagi.py`; it then evaluates the result with the thin-wire MoM (using a plain dipole driven element re-resonated for X = 0).

## Corner reflector antennas

**Idea.** A dipole is placed in front of two flat reflecting sheets that meet at an angle α (usually 90°). The sheets behave as mirrors, so the dipole and its images form a small array whose beam points out of the corner. The sheets can be made of rods parallel to the dipole, spaced ≤ 0.1λ apart; the rods only reflect the polarization parallel to them. Kraus introduced the antenna in 1940, and Balanis §15.3 gives the analysis [9], [10]. Compared with a Yagi it has no critical element lengths, a wide bandwidth, a high F/B and a convenient feed impedance. It is bulkier for the same gain.

**Image theory (90°, infinite PEC sheets).** For a dipole at distance S from the apex there are three images: one at the opposite corner (same sign, distance 2S) and two on the sheets (opposite sign, distance S√2). In the front wedge |φ| < 45° the field is the dipole element pattern multiplied by
$$AF(\theta,\phi)=2\big[\cos(kS\sin\theta\cos\phi)-\cos(kS\sin\theta\sin\phi)\big],$$
and it is zero elsewhere. The input impedance follows from the mutual impedances of [§ Level 2](#level-2--mutual-impedance-induced-emf-and-mom): $Z_\text{in}=Z_{11}-2Z_{12}(S\sqrt2)+Z_{12}(2S)$. The script integrates the directivity numerically over the wedge only. With an exact λ/2 dipole it gives D = 12.4/12.1/11.8/11.3/11.4 dBi and Z = 48 + j100, 96 + j97, 126 + j59, 115 + j12 and 73 − j6 Ω for S = 0.3/0.4/0.5/0.6/0.7λ. At S = 0.5λ, R ≈ 126 Ω agrees with Kraus's classic ≈ 125 Ω.

**NEC with a real rod screen.** This uses a 433 MHz vertical dipole re-resonated in place, 6 mm rods 0.75λ long at 0.08λ spacing, and sides 2S (`tools/verify/s12_corner_omnicp.py` §1):

| S/λ | Gain dBi | F/B dB | HPBW H × E (°) | R at resonance (Ω) | Image theory D (dBi) |
|---|---|---|---|---|---|
| 0.30 | 8.76 | 28.0 | 74 × 64 | 42 | 12.37 |
| 0.40 | 9.41 | 31.9 | 58 × 68 | 89 | 12.14 |
| 0.50 | 9.70 | 25.3 | 50 × 70 | 133 | 11.81 |
| 0.60 | 9.80 | 22.1 | 42 × 76 | 144 | 11.34 |
| 0.70 | 9.61 | 19.2 | 34 × 90 | 94 | 11.44 |

The finite screen costs about 2 dB against image theory. I had pre-registered "within 1.5 dB" for this geometry, and that check failed (9.70 vs 11.81 dBi). Gain depends on screen size at S = 0.5λ: sides × rod length 1λ × 0.75λ gives 9.7 dBi, 1λ × 1λ gives 10.2 dBi and 1.5λ × 1λ gives 11.1 dBi. Larger screens of 2λ × 1.25λ and 3λ × 1.5λ give 12.9 and 13.4 dBi, more than image theory. The long rods then carry collinear-like currents that narrow the E-plane beam, which the dipole-element image model does not contain. The average-gain test gives 1.000 for every model.

**Build numbers (S = 0.5λ).**
- **433 MHz:** dipole 319 mm at 346 mm from the apex; sides 692 mm; 25 rods of 519 mm (6 mm diameter) every 55 mm. Across 405–460 MHz the gain is 9.5–9.85 dBi and the VSWR referred to 133 Ω is ≤ 1.33.
- **915 MHz:** dipole 152 mm at 164 mm; sides 328 mm; rods 246 mm × 2 mm every 26 mm. This gives 9.65 dBi and 133 Ω.
- **Matching:** feed 133 Ω through a λ/4 75 Ω section (42 Ω, VSWR 1.2) and a choke, or move the dipole in to S ≈ 0.32λ for ≈ 50 Ω at ≈ 9 dBi.

**When to choose it for the ground station.** It has a 50° × 70° beam at 9.7 dBi, which is about a 3-element Yagi's gain but with 10 dB more F/B and no tuning. That makes it a good fixed antenna aimed at the expected flight azimuth and mid elevation, and a good antenna for noise rejection behind the station. It is linear, so a rolling rocket's linear antenna fades through it twice per roll. For CP, a solid or mesh corner fed with a turnstile works, but a rod screen does not, because it reflects only one polarization. For no pointing at all, use an omni-CP antenna, compared in [polarization § omni-CP](antenna-polarization-and-circular-polarization.md#omni-cp-antennas-for-overhead-passes-turnstile-eggbeater-lindenblad). Use a crossed Yagi when the margin needs > 10 dBic.

## Two-element Yagis, and F/B, F/R and F/S

**Reflector or director?** NEC (`tools/verify/s12_practicalities.py` §D) uses 433 MHz, 6 mm elements and a driven element resonant alone (319.2 mm). At each spacing the parasitic length is optimised for forward gain:

| Spacing (λ) | Reflector type: L_p/λ, G dBi, F/B dB, Z_in (Ω) | Director type: L_p/λ, G dBi, F/B dB, Z_in (Ω) |
|---|---|---|
| 0.05 | 0.481, 7.23, 6.0, 3.6 − j5.5 | 0.461, 7.42, 9.5, 4.2 − j21.6 |
| 0.10 | 0.475, 7.14, 6.0, 14.3 + j14.6 | 0.447, 7.26, 6.7, 13.7 − j11.6 |
| 0.15 | 0.468, 6.97, 5.9, 30.6 + j29.3 | 0.434, 6.71, 4.7, 26.6 − j0.7 |
| 0.20 | 0.462, 6.73, 5.6, 49.2 + j35.9 | 0.423, 5.94, 2.7, 39.8 + j8.6 |
| 0.25 | 0.461*, 6.36, 6.1, 70 + j35 | 0.413, 5.13, 1.2, 52 + j14 |

\* The length hit the search bound (= driven-element length), so a "reflector" is no longer longer than the driven element here.

The maximum gain of both types (≈ 7.2–7.4 dBi, about 5 dBd) occurs at very close spacing, where the feed resistance is only a few ohms. That is the super-directive limit: losses and matching eat the gain. Gain falls slowly with spacing. The reflector type holds its gain better at wider spacing (6.7 dBi and 49 Ω at 0.2λ), while the director type collapses (5.9 dBi, F/B 2.7 dB). In practice, use a **reflector at 0.15–0.2λ** for a direct 30–50 Ω feed and a forgiving build, and a **director at 0.1λ** for the last 0.1–0.3 dB with a hairpin or gamma match. Either way the 2-element F/B is only 5–10 dB; a third element is what brings F/B to 15+ dB.

**F/B, F/R and F/S.**
- **F/B** compares the forward gain with the gain exactly 180° behind.
- **F/R** (front-to-rear) compares it with the worst lobe anywhere in the rear half-space. It is the more honest figure for interference.
- **F/S** compares it with the gain at 90°. In the element plane (E-plane) F/S is infinite for any Yagi, because the dipole element has a null along its axis. In the H-plane (90° above or below a horizontal Yagi) it is finite.

NEC (§C) gives two results. The KB 3-element Yagi has 9.25 dBi, F/B = F/R = 13.7 dB and H-plane F/S 18.3 dB. The 11-element DL6WU Yagi has 14.31 dBi, F/B = F/R = 17.2 dB and F/S 21.3 dB. For a vertically polarised ground-station Yagi, the H-plane is horizontal. Its F/S (18–21 dB) therefore sets how much a signal 90° off the boresight azimuth is rejected. The element-plane null points straight up and down.

## Design equations & rules of thumb

| Quantity | Rule | Validity | Example |
|---|---|---|---|
| Gain vs boom | G ≈ 9.2 + 3.39 ln(B/λ) dBd | DL6WU, 2.2–39λ | 2.49λ → 14.4 dBi (MoM 14.2) |
| 3-el Yagi | ≈ 7.5–9.2 dBi, F/B 10–25 dB | boom 0.3–0.4λ | MoM 9.15 dBi / 15 dB / 11 Ω (needs a match); direct 50 Ω feed, band-constrained: 8.55 dBi / 15 dB / VSWR 1.5 (NEC, `sim2_nec_yagi_optimise.py`) |
| Reflector length | ≈ 0.48–0.50λ | thin elements | 336 mm at 433 MHz (6 mm) |
| Directors | ≈ 0.44→0.38λ, tapered | — | 297→267 mm (433 MHz) |
| Element tolerance | ±0.003λ | DL6WU | ±2 mm @433, ±1 mm @915 MHz |
| Boom correction | DL6WU fit (≈ 0.5–0.7 × boom Ø for bonded) | BD < 0.055λ | 20 mm boom @433: ≈ +11 mm |
| Beamwidth | HPBW ≈ 30 − 3.14(G_dBd−14)° | DL6WU correlation | 12.3 dBd → 35° (MoM 36°) |
| Stacking distance | D = λ/(2 sin(B/2)) (DL6WU/G3SEK); 51/HPBW(°) λ is 11–14 % closer (lower lobes, −0.2–0.3 dB) | two long Yagis | 11-el 433 MHz: 1.64λ E / 1.50λ H; 51/HPBW → 1.44/1.31λ ([12](../12-phased-arrays/stacking-and-arraying-yagis.md)) |
| Corner reflector (90°) | S = 0.5λ, sides ≥ 2S, rods ≤ 0.1λ apart, rods ≥ 0.75λ | rod screen | 9.7 dBi, F/B 25 dB, R ≈ 133 Ω |
| 2-element Yagi | spacing 0.1–0.15λ; reflector +2–3 % / director −3–6 % vs DE | NEC | 7.0–7.3 dBi, F/B 5–7 dB, Z 14–31 Ω |
| Far field for testing | 2B²/λ | — | 1.72 m boom: 8.6 m |
| LPDA apex | cot α = 4σ/(1−τ) | — | τ 0.90, σ 0.168 → α = 8.5° |
| LPDA optimum σ | σ_opt = 0.243τ − 0.051 | Carrel | τ 0.9 → 0.168 |
| LPDA active region | B_ar = 1.1 + 7.7(1−τ)²cot α | Carrel | 1.62 |
| LPDA elements | N = 1 + ln(B·B_ar)/ln(1/τ) | — | 400–1000 MHz → 15 |
| LPDA boom | (λ_max/4)(1 − 1/B_s)cot α | — | 0.95 m |

(The boom-correction number above is an illustration of the formula's magnitude: BD = 20/692 = 0.0289 → BC₁ ≈ 0.54 of the boom diameter → ≈ 10.7 mm; always compute for your boom.)

## Worked examples

### Example 1 — 433 MHz ground-station Yagi, 11 elements (DL6WU, 6 mm elements, non-metallic boom or elements insulated clear of the boom)
From `tools/verify/ant_yagi.py` (dimensions in mm, positions from the reflector):

| Element | Position | Length |
|---|---|---|
| Reflector | 0 | 336.2 |
| Driven element (plain dipole, resonated in MoM) | 138 | 335.1 (folded-dipole per DL6WU: 329.8) |
| D1 | 190 | 297.1 |
| D2 | 315 | 293.0 |
| D3 | 464 | 288.9 |
| D4 | 637 | 285.2 |
| D5 | 831 | 281.9 |
| D6 | 1039 | 279.1 |
| D7 | 1257 | 276.7 |
| D8 | 1485 | 274.5 |
| D9 | 1724 | 272.6 |

MoM: **D = 14.20 dBi** (DL6WU estimate 14.44 dBi), F/B = 16.3 dB, HPBW 36.4° (element plane) × 39.8°, Z_in (plain dipole DE) = **52 Ω** — conveniently close to 50 Ω; with DL6WU's folded dipole DE you would instead use a 4:1 coax balun. Energy check P_rad/P_in = 1.001.
Practical: 1.8 m boom (allow overhang); build the elements to ±2 mm; if you use a 20 mm aluminium boom with elements bonded through it, add the DL6WU boom correction (≈ 11 mm per element for that boom).

### Example 2 — 915 MHz ground-station Yagi, 11 elements (4 mm elements)
Positions (mm): 0, 66, 90, 149, 220, 301, 393, 491, 595, 703, 816. Lengths: R 158.6; DE (plain, resonated) 158.0 (folded 155.0); directors 138.4, 136.5, 134.4, 132.5, 130.8, 129.4, 128.2, 127.1, 126.2.
MoM: **14.26 dBi**, F/B 16.7 dB, HPBW 36° × 39°, Z_in 50.0 Ω. A 16-element version on a 1.45 m boom reaches **16.25 dBi** (HPBW 29° × 31°).

### Example 3 — A handheld 3-element 433 MHz Yagi (for recovery direction-finding and close-in tracking)
MoM optimisation (6 mm elements, gain with F/B ≥ 15 dB): reflector 336.6 mm, driven element 314.7 mm (plain dipole, resonated), director 296.3 mm; reflector–DE 88 mm, DE–director 154 mm (boom 242 mm). **9.15 dBi, F/B 15.0 dB, HPBW 59° × 84°**, Z_in ≈ 11 Ω. Match options: (a) folded-dipole driven element (≈ ×4 → ~44 Ω, then a 1:1 choke), (b) hairpin (shunt inductor) with a slightly shortened DE, (c) gamma match. Commercial handheld 3-element 435 MHz Yagis of similar size are used with Altus Metrum receivers for recovery [7]. The broad beam makes it easy to keep a rocket in view by hand; the long Yagis above need a tracker or a well-predicted trajectory.

*Cross-check (W5-S11, 2026-10-13; `tools/verify/sim2_nec_yagi_optimise.py`, [NEC modelling Example 4](../16-simulation-tools/nec-antenna-modelling.md)).* A PyNEC optimisation of the same problem with 4 mm rod, the driven element fed **directly** from 50 Ω, and the objective held over 433.05–434.79 MHz (F/B ≥ 15 dB, VSWR ≤ 1.5) converged (differential evolution and particle swarm within 0.02 dB) to **8.55 dBi**, Z 33.8 + j1.4 Ω, boom 0.45λ. The 9.15 dBi above is a single-frequency, 6 mm, 11 Ω design whose matching network is not modelled. The two are consistent: ≈ 0.6 dB is the price of a direct 50 Ω feed and a band-wide specification. An unconstrained run reaches 9.90 dBi with a 3.8 Ω superdirective feed, which is not buildable. A ±1 mm / ±2 mm tolerance Monte Carlo of the 8.55 dBi design cost ≤ 0.11 dB. For link budgets, use **≈ 8.5 dBi** unless the matched design is built and measured.

### Example 4 — How much gain does a ground station need?
With the rocket's axial dipole, a 10 km apogee and a 2 km ground offset, the look angle is 11° off the rocket's axis and the rocket-side gain is ≈ −14 dBi (see [antennas-on-rockets](antennas-on-rockets.md)). At 433 MHz with 33 dBm, a 9 dBi Yagi (≈ 8.5 dBi for a directly fed build — 0.5 dB less margin) still gives ≈ 50 dB margin over LoRa SF9 sensitivity in free space (`tools/verify/ant_rocket.py`) — the licensed-power case; at Singapore's licence-exempt 10 mW e.r.p. (≈ 10 dBm into the dipole) the margin is ≈ 27 dB ([19](../19-regulations-safety/singapore-imda-rules.md)). So *beamwidth and polarization*, not raw gain, usually dominate the ground-antenna choice for amateur altitudes; long Yagis matter for high-altitude/long-range flights and for recovery-phase links near the ground (Fresnel-zone and terrain losses — [fresnel zones](../09-propagation-link-budget/fresnel-zones-los-radio-horizon.md)).

### Example 5 — LPDA for 400–1000 MHz (covers 433 and 868/915)
τ = 0.90, σ = σ_opt = 0.1677 → cot α = 6.71 (α = 8.5°), B = 2.5, B_ar = 1.617, B_s = 4.04, N = 14.3 → **15 elements**, longest element λ(400 MHz)/2 = 375 mm, shortest ≈ 375 × 0.9¹⁴ ≈ 86 mm, boom ≈ **0.95 m**. Expected gain ≈ 7.5–9 dBi (see note on Carrel's contours below). The feeder (a pair of square tubes) is chosen for ≈ 50–100 Ω input with the formula in [5]; a 1:1 balun or the "infinite balun" (coax run inside one feeder tube) completes it.

## Practical notes
- **Build tolerance**: element length errors of +1 % on the directors shift the design toward a lower frequency and can reduce gain sharply at the top of the band; DL6WU designs are forgiving but not magic. Measure with a steel rule, not a tape.
- **Element mounting**: insulated elements above the boom (≥ one boom radius clearance) need no correction; bonded through-boom elements need the full DL6WU correction.
- **Driven element and balun**: feed with a 1:1 current choke (ferrite on the coax at the feed) or a λ/2 coax 4:1 balun for a folded dipole ([baluns](antenna-matching-and-baluns.md)). Common-mode current on the coax skews the pattern and degrades F/B.
- **Weather**: aluminium tube + nylon insulators; seal the feed box; stainless hardware.
- **Mast interaction**: mount horizontally-polarized Yagis ≥ ~λ/2 in front of a metal mast; vertical polarization with a metal mast *parallel* to the elements is harmful (couples strongly) — use a non-metallic mast section.
- **Crossed Yagi for CP**: two identical Yagis on one boom at 90°, one displaced λ/4 along the boom *or* fed with a λ/4 (90°) phasing line; combine with a 2-way splitter/hybrid. Handedness depends on which is delayed; build with a switch for RHCP/LHCP when unsure (reflections and the rocket's own antenna may flip or mix senses — [polarization](antenna-polarization-and-circular-polarization.md)).
- **Carrel's LPDA gain contours were optimistic**: later analyses (Butson & Thompson 1976 and subsequent LPDA literature summarised by Balanis §11.4 [1] and the hamwaves notes [5]) found Carrel's directivity contours ~1–2 dB too high; use NEC to predict LPDA gain.

## Common mistakes & misconceptions
- **"Double the elements, double the gain (+3 dB)."** Gain ~ ln(boom), so doubling boom length adds only ≈ 2.3 dB; doubling the *element count* at fixed boom adds nearly nothing.
- **"More gain is always better for a ground station."** A 30–36° beam must be kept on the rocket; losing lock costs far more than 3 dB. Choose gain after deciding how you will point.
- **"Yagi element lengths from a calculator are exact."** They assume a boom treatment and element diameter; changing either without correction detunes the antenna.
- **"F/B ratio is the same as gain."** They are optimised in conflict; max-gain and max-F/B designs differ.
- **"The driven element must be resonant alone."** Its impedance is set *in situ* by the parasitic elements; resonate it in the array.
- **"A log-periodic is a wideband Yagi with the same gain."** For equal boom length an LPDA has 2–5 dB less gain than a Yagi; it trades gain for bandwidth.
- **"The longer element of a 2-element Yagi is always better."** The director version has slightly more peak gain (7.4 vs 7.2 dBi), but only at spacings where Z is a few ohms. At practical spacings the reflector version is the more forgiving one (NEC table above).
- **"F/B = 25 dB means nothing comes from behind."** F/B is one direction. Check F/R (the worst rear lobe) and the H-plane F/S.
- **"A corner reflector's gain is the textbook 12 dBi."** That is for infinite sheets. A 1λ × 0.75λ rod screen gives 9.7 dBi; you need ≈ 1.5λ × 1λ for 11 dBi.
- **"51/HPBW and λ/(2 sin(B/2)) are the same stacking rule."** They differ by 11–14 %. The second gives ≈ 0.2–0.3 dB more gain and the first gives lower stacking lobes ([12](../12-phased-arrays/stacking-and-arraying-yagis.md)).
- **Polarization mismatch**: a horizontally mounted Yagi receiving a vertical whip on a rocket on the pad: −20 dB or worse (forum reports of "no signal on the pad" — anecdotal — usually trace to this).

## How to simulate / verify
- `python3 tools/verify/ant_yagi.py` (≈ 3–4 min): mutual-impedance check, DL6WU designs at 433/915 MHz evaluated by MoM, 3-element optimisation, LPDA equations. Change `cases` for your boom length and element diameter.
- NEC-2 (4nec2/xnec2c): segment each element into ≥ 21 segments (≤ λ/20), keep segment length/radius > 8; NEC-2 is inaccurate for **stepped/tapered-diameter** elements (telescoping tubes) — use NEC-4, EZNEC's Leeson correction, or keep constant diameter ([simulation](antenna-simulation-nec-openems.md)).
- `python3 tools/verify/s12_corner_omnicp.py` (≈ 5 min): corner reflector vs S and screen size, with an image-theory comparison; omni-CP antennas and a crossed 7-element Yagi (output `s12_corner_omnicp_output.txt`).
- `python3 tools/verify/s12_practicalities.py` §C–D: F/B, F/R and F/S of the 3- and 11-element Yagis; 2-element reflector vs director sweep.
- Measure: SWR across the band with the antenna on its mast; F/B and pattern with a signal source ≥ 2B²/λ away (8.6 m for the 11-el 433 MHz) — see [antenna measurement](antenna-measurement.md) (SDR-based pattern measurement is adequate).

## Open questions / gaps
- The Butson & Thompson (1976) correction to Carrel's gain contours is cited secondarily; the primary paper was not read.
- Crossed-Yagi CP axial-ratio performance vs phasing-line errors could be added to `ant_polarization.py`.
- The corner-reflector sources (Kraus 1940, Balanis §15.3) are cited from standard knowledge; the NEC/image numbers here are the KB's own.
- A 5-element mid-size design (≈ 1λ boom, 10–11 dBi) for handheld tracking could be optimised with the MoM and added.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — §8.6 (mutual impedance, induced-EMF formulas), §10.3 (Yagi-Uda analysis), §11.4 (log-periodic dipole arrays, Carrel design procedure). (textbook)
2. H. Yagi, "Beam transmission of ultra short waves," *Proc. IRE* 16, 1928; S. Uda's earlier Japanese papers (1926). (peer-reviewed, historical)
3. G. Hoch (DL6WU), "Extremely long Yagi antennas," *VHF Communications* 3/1982, and "More gain with Yagi antennas," *VHF Communications* 4/1977 — design data as implemented in *DL6WU.BAS* by J. Haigwood KY4Z, B. Stein W6NBI and I. White G3SEK (spacing table, director curve-fit constants, reflector and DE formulas, boom correction, gain and beamwidth correlations, ±0.003λ tolerance). http://www.ifwtech.co.uk/g3sek/diy-yagi/ (design program/data; primary articles not read)
4. L. B. Cebik (W4RNL), "Appreciating DL6WU wide-band long-boom Yagi design" — NEC results for 432 MHz DL6WU designs (12/19/26/32 el), 2:1 SWR 405–452 MHz. https://antenna2.github.io/cebik/content/vhf/wu.html (expert article)
5. R. L. Carrel, "The design of log-periodic dipole antennas," *IRE Int. Convention Record*, pt. 1, pp. 61–75, 1961 (PDF hosted at hamwaves.com); hamwaves.com LPDA calculator documentation (τ, σ, σ_opt = 0.243τ − 0.051, cot α, B_ar, N, feeder Z). https://hamwaves.com/lpda/en/index.html (peer-reviewed / design notes)
6. P. E. Mayes, R. L. Carrel, "Log-periodic resonant-V arrays," and D. E. Isbell, "Log periodic dipole arrays," *IRE Trans. Antennas Propag.* AP-8, pp. 260–267, 1960. (peer-reviewed, cited via Balanis)
7. Altus Metrum owner's manual — handheld 440-3/440-5 Yagis used for rocket recovery at 435 MHz. https://altusmetrum.org/AltOS/doc/altusmetrum.html (manufacturer manual)
8. This repository: `tools/verify/ant_yagi.py`, `tools/verify/ant_mom_wire.py`, `tools/verify/s12_corner_omnicp.py`, `tools/verify/s12_practicalities.py`, `tools/verify/e8_yagi_stack.py`. (verification)
9. J. D. Kraus, "The corner-reflector antenna," *Proc. IRE* 28(11), 513–519, 1940; Kraus & Marhefka, *Antennas for All Applications*, 3rd ed., 2002, ch. 12 — image analysis, S ≈ 0.5λ, R ≈ 125 Ω. (peer-reviewed / textbook; cited, not re-read)
10. C. A. Balanis, *Antenna Theory*, 4th ed., 2016, §15.3 (corner reflectors: images, gain vs spacing, screen size). (textbook)
11. ARRL, *The ARRL Antenna Book*, 24th ed., 2019 — 2-element parasitic arrays (reflector vs director, spacing, feed impedance), F/B and F/R definitions. (handbook; cited)
12. I. White (G3SEK), "Stacking Yagi antennas," VHF/UHF Long Yagi Workshop — DL6WU stacking formula D = λ/(2 sin(B/2)); see [12/stacking](../12-phased-arrays/stacking-and-arraying-yagis.md). (amateur engineering literature, read by W5-E8)
