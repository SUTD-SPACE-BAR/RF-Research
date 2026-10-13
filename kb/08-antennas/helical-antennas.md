---
title: Helical antennas — normal and axial mode, realistic axial-mode gain (Kraus vs King & Wong vs Emerson), quadrifilar helix
domain: 08-antennas
slug: helical-antennas
tags: [helix, axial-mode, normal-mode, circular-polarization, kraus, king-wong, emerson, qfh, quadrifilar-helix, ground-station, gnss]
prerequisites: [antenna-fundamentals.md, antenna-polarization-and-circular-polarization.md, dipoles-and-monopoles.md]
related: [gnss-antennas.md, antennas-on-rockets.md, yagi-uda-and-log-periodic.md, small-antenna-limits.md, antenna-simulation-nec-openems.md, ../12-phased-arrays/array-factor-linear-arrays.md, antenna-identification-guide.md]
level: mixed
confidence: high
last_updated: 2026-10-02
---

# Helical antennas

## Questions this page answers
- What is the difference between a normal-mode and an axial-mode helix?
- How do I design an axial-mode helix for 435 MHz or 2.4 GHz?
- Why do calculators say my 10-turn helix has 16–17 dBi when it measures ~13 dBic?
- Which formula for helix gain should I trust — Kraus, King & Wong, or Emerson?
- How big a ground plane does a helix need?
- How do I match a helix (≈100–150 Ω) to 50 Ω?
- Which winding direction gives RHCP?
- What is a quadrifilar helix (QFH) and why is it used for weather satellites and some GNSS antennas?
- Is a helix a good ground-station antenna for a rolling rocket?

## TL;DR
- **Normal mode** (circumference C ≪ λ): the helix is a compact loaded monopole/dipole radiating broadside (rubber-duck whips); it is CP only when C² = 2Sλ (Wheeler's condition) and usually linear in practice.
- **Axial mode** (Kraus): 3/4 < C/λ < 4/3, pitch angle 12–15°, N > 3 turns, over a ground plane ≥ ~λ/2. It radiates a CP end-fire beam along its axis with AR typically < 1.5 dB, over nearly an octave of impedance bandwidth, with R_in ≈ 100–150 Ω.
- **Kraus's gain formula G = 15(C/λ)²NS/λ is optimistic by 3–5 dB.** King & Wong's measurements (IEEE TAP 1980) gave gain factors 4.2–7.7 instead of 15 [2]; Emerson's 10 000-case NEC study found Kraus "optimistic by up to 4 or 5 dB" and fitted G_max(dBi) = 10.25 + 1.22L − 0.0726L² (L = axial length in λ, 2–7λ) [3].
- **Our own MoM** (`tools/verify/ant_mom_general.py`): 10 turns, C = 1.1λ, α = 12.8°, over a PEC ground: **12.6–12.7 dBic** on axis (converging with segmentation); King & Wong formula 13.2; Emerson 12.9; Kraus 16.6. Realistic design numbers: 435 MHz, 10 turns = 1.72 m long, **≈ 13 dBic** — not 16.6.
- Gain rises only as ~0.8–1.2 dB per extra wavelength of length (King & Wong: doubling N gives less than 3 dB).
- **Handedness**: a helix wound like a right-hand screw (advancing away from the ground plane) radiates **RHCP** (IEEE) along +axis; our MoM gives RHCP 12.6 dBic vs LHCP −16.5 dBic on axis for a right-hand winding. Reflection off a dish or the ground reverses the sense.
- The **quadrifilar helix (QFH)** (Kilgus 1968+) is a resonant CP antenna with a broad cardioid/hemispherical pattern — excellent for satellites overhead and for multi-orientation GNSS, but narrowband and tolerance-sensitive.

## Intuition (no math)
**Normal mode.** If the helix is small (circumference ≪ λ), each turn is a tiny loop (radiating like a magnetic dipole along the axis) and the pitch between turns is a tiny straight wire (an electric dipole along the axis). Both radiate broadside to the axis, with orthogonal polarizations and 90° apart in phase. When their strengths are equal you get CP; usually the dipole part dominates and it is effectively a shortened, inductively loaded monopole — the familiar stubby whip.

**Axial mode.** When each turn is about one wavelength around, the current travels along the wire as a wave and the phase advances by ~360° per turn — plus a little more. Seen from the end of the helix, the current at any instant makes a full turn of rotation per wavelength of wire, so the field it radiates along the axis rotates: circular polarization. Each turn acts like an element of an end-fire array, with the wave along the helix slowed so that contributions from successive turns add in phase along the axis (close to the Hansen–Woodyard increased-directivity condition). The ground plane (or a cup) reflects the backward wave and helps launch the forward mode.

**Why Kraus's gain is too high.** Kraus derived his gain from measured beamwidths using D ≈ 41 253/HPBW², which assumes all power is in a clean main lobe. Real helices have significant sidelobes and a back lobe, so the true gain–beamwidth product is lower (King & Wong measured G·HPBW² = 24 000–31 500, not 41 253) [2]. Kraus also assumed the phase velocity always adjusts itself to the optimum; in reality it does so only approximately and only for some lengths.

## The math

### Level 1 — geometry and design formulas
Symbols: D = helix diameter (wire centre to centre), C = πD circumference, S = turn spacing (pitch), α = pitch angle = arctan(S/C), N = number of turns, L = NS axial length, λ = free-space wavelength.

| Formula | Source | Validity |
|---|---|---|
| G_Kraus = 15 (C/λ)² N S/λ (linear) | Kraus 1947/1988 [1] | historically for 12° < α < 14°, 3/4 < C/λ < 4/3, N > 3 — **optimistic** |
| HPBW_Kraus = 52/[(C/λ)√(NS/λ)] degrees | Kraus [1] | measured 61–70 instead of 52 (King & Wong) |
| G_KW = 8.3 (πD/λ_p)^(√(N+2)−1) (NS/λ_p)^0.8 [tan 12.5°/tan α]^(√N/2) | King & Wong 1980 [2] | peak gain, 12° < α < 15°, 3/4 < C/λ < 4/3, N > 3 (measured with a cavity backing) |
| G_max(dBi) = 10.25 + 1.22L − 0.0726L² | Emerson 1995 [3] | L = 2–7λ, optimum C at each L (NEC-2) |
| R_opt/λ = 0.2025 − 0.0079L + 0.000515L² | Emerson [3] | optimum radius → C_opt ≈ 1.19λ (L = 2) … 1.08λ (L = 7) |
| R_in ≈ 140 (C/λ) Ω | Kraus [1] | axial feed; depends strongly on feed geometry |
| AR ≈ (2N+1)/(2N) | Kraus (Hansen–Woodyard phasing) | on axis, ideal |

Comparison (C/λ = 1.10, α = 12.8°, `tools/verify/ant_helix.py`):

| N | L/λ | Kraus | King & Wong | Emerson | Kraus − KW | Kraus − Emerson |
|---|---|---|---|---|---|---|
| 5 | 1.25 | 13.6 | 10.5 | — | 3.0 | — |
| 8 | 2.00 | 15.6 | 12.3 | — | 3.3 | — |
| 10 | 2.50 | 16.6 | 13.2 | 12.9 | 3.3 | 3.7 |
| 15 | 3.75 | 18.3 | 14.9 | 13.8 | 3.5 | 4.5 |
| 20 | 5.00 | 19.6 | 16.1 | 14.5 | 3.5 | 5.0 |
| 25 | 6.25 | 20.6 | 17.0 | 15.0 | 3.5 | 5.5 |
(dBi / dBic for the co-polar sense.)

### Level 2 — why axial mode works, and the realistic gain
**Travelling-wave phasing.** Let the current travel along the helix wire with phase velocity v = pc. Between adjacent turns the wire length is L_t = √(C² + S²). For the fields of successive turns to add along the axis with the Hansen–Woodyard extra phase δ = π/N, the phase difference must satisfy
$$\frac{2\pi L_t}{p\lambda}-\frac{2\pi S}{\lambda}=2\pi+\frac{\pi}{N}\;\Rightarrow\;p=\frac{L_t/\lambda}{S/\lambda+1+\frac{1}{2N}} .$$
For C = λ, α = 12.8° (S = 0.227λ, L_t = 1.026λ) and N = 10: p ≈ 0.80. Measurements show the helix wave naturally adopts a velocity close to this over a wide band — the physical reason for the axial mode's broad bandwidth (Kraus [1]). The same phasing makes the axial field rotate once per turn → CP; the Hansen–Woodyard excess phase gives AR = (2N+1)/2N.

**Directivity of an end-fire array.** An N-element end-fire array with Hansen–Woodyard phasing has D ≈ 7.28·(NS/λ) (compared with 4NS/λ ordinary end-fire — see [array factor](../12-phased-arrays/array-factor-linear-arrays.md)); multiplying by an element factor that squeezes the pattern further, Kraus arrived at the 15(C/λ)²NS/λ form via G ≈ 41 253/HPBW² with HPBW = 52/[(C/λ)√(NS/λ)]. Both steps are optimistic: the measured HPBW constant is 61–70 and the measured G·HPBW² is 24 000–31 500 [2].

**Our MoM check.** We modelled a right-hand helix (wire radius 0.005λ, 12/16/24 segments per turn) over an infinite PEC ground via images, fed by a short vertical wire at the ground (0.02λ):

| Case (435 MHz) | Axial D (RHCP) | Z_in | Notes |
|---|---|---|---|
| N = 10, C = 1.10λ, 12 seg/turn | 12.37 dBic | 101 − j66 Ω | |
| N = 10, C = 1.10λ, 16 seg/turn | 12.56 dBic | 101 − j64 Ω | LHCP on axis −16.5 dBic (AR ≈ 0.6 dB) |
| N = 10, C = 1.10λ, 24 seg/turn | 12.68 dBic | 102 − j63 Ω | converging to ≈ 12.8 |
| N = 10, C = 0.90 / 1.00 / 1.20 / 1.30λ | 11.1 / 11.7 / 13.4 / 11.1 dBic | 116 → 79 Ω | peak near C ≈ 1.2λ |
| N = 6, C = 1.10λ | 10.6 dBic | 99 − j69 Ω | |

These sit between King & Wong and Emerson, 3.5–4 dB below Kraus: **three independent methods (measurement, Emerson's NEC, our MoM) agree that Kraus's formula overestimates.** The capacitive reactance comes from our simple feed geometry; real builds compensate it with the feed-strap/taper (below).

### Level 3 — reconciling the sources, and limits
- **What exactly is being compared.** Kraus's "15" was for *directive gain* (lossless); King & Wong measured *gain* with a CP source on a 30–60 ft range, including a 10.3 in cavity backing and a microstrip taper transformer; Emerson computed *NEC directivity/gain* for lossless and lossy wire over various grounds; our MoM computes directivity for PEC wire over an infinite PEC ground. Loss in copper helices is small (Emerson: wire diameter and resistance had minimal effect) so these are comparable to ~0.3 dB. The large discrepancy is therefore a real overestimate in Kraus's formula, not a definitional difference.
- **Frequency of peak gain.** King & Wong: peak at C/λ_p ≈ 1.135 for 30-in fixed-length helices, from 1.155 (N = 5) to 1.07 (N = 35); gain rises roughly as f^2.5–f^6 below the peak and falls sharply above it [2]. Design C ≈ 1.1–1.2λ at the *centre* of the wanted band, not C = λ.
- **Ground plane.** Emerson: a λ/2 square ground ≈ an infinite ground; a radial-wire ground costs ≈ 3.5 dB [3]. Cups (cavity backing) improve AR and front-to-back.
- **Bandwidth.** King & Wong's 3 dB gain bandwidth shrinks with N (roughly ±15 % for short helices down to ±8 % for long) [2]; impedance and AR bandwidths are wider.
- **Tapered ends** improve VSWR, AR and pattern (King & Wong, Wong & King [2]).
- **Very long helices** (L > 7λ) saturate; array several helices instead ([12-phased-arrays](../12-phased-arrays/planar-arrays-element-pattern-coupling.md)).

## Normal-mode helix (compact whips)
Treat one turn as a small loop of area A = πD²/4 plus a short dipole of length S. Their far fields (broadside) are E_φ ∝ ηk²A·I/(4πr) (loop) and E_θ ∝ jηkS·I/(4πr) (dipole), in quadrature. The axial ratio is
$$\text{AR}=\frac{|E_\theta|}{|E_\phi|}=\frac{2S\lambda}{C^2},$$
so CP requires C = √(2Sλ) (Wheeler 1947; Kraus [1]). Practical normal-mode helices (stubby 433/868 MHz whips, GNSS "helix" chips excepted) are far from this and radiate essentially linear polarization like a monopole of the same height, with the coil providing inductive loading. Their efficiency is governed by the loaded-monopole physics on [dipoles-and-monopoles](dipoles-and-monopoles.md#loaded-short-monopoles-stubby-rubber-duck-helical-whips) and the bounds on [small-antenna-limits](small-antenna-limits.md).

## Quadrifilar helix (QFH)
- **Structure**: two bifilar helical loops (each two diametrically opposite half- or full-turn helical wires joined by radials at top and bottom), rotated 90° and fed in phase quadrature (Kilgus 1968–1975 [4]). The superposition behaves like crossed dipoles + crossed loops, producing CP over a very wide beam (cardioid to nearly hemispherical depending on height/diameter ratio and turns).
- **Self-phasing**: instead of a 90° hybrid, the two loops are made different sizes so one resonates slightly above and one slightly below the operating frequency; at the operating frequency their currents are ≈ +45° and −45° — exactly the two-mode condition analysed for CP patches (mode split ≈ f₀/Q; see [patch-antennas](patch-antennas.md#level-2--the-two-models)). Amateur 137 MHz NOAA-APT designs use loops differing by several percent in length and an "infinite balun" (coax run down one leg) [5].
- **Pattern**: broad, with low-elevation coverage and strong rejection of the opposite sense and of the back hemisphere — which is why it suits LEO satellites and multi-orientation GNSS (Sarantel/Maxtena ceramic QFH-type GNSS antennas; u-blox notes helix GNSS antennas give "robust" performance where orientation varies, but pick up more multipath than a patch on a large ground) [6].
- **Handedness**: set by the winding sense *and* which loop is the larger (leading) one; builders often get LHCP by mistake. Check with a known RHCP source or an SDR on a real satellite.
- **Sensitivity**: resonant and narrowband (a few %); dimensional tolerances of a few mm at 137 MHz and sub-mm at 1.5 GHz matter; dielectric-loaded versions are even more sensitive (u-blox [6]).

## Design equations & rules of thumb

| Item | Rule | Example (435 MHz) |
|---|---|---|
| Circumference | C ≈ 1.1–1.2λ at band centre | 758–828 mm (D ≈ 241–264 mm) |
| Pitch | α ≈ 12–14° (S ≈ 0.23–0.27λ) | S ≈ 172 mm |
| Turns / gain | use Emerson or KW, not Kraus | 10 turns (1.72 m) → ≈ 13 dBic |
| Ground | ≥ 0.5λ square or a cup (≈ 0.25λ deep) | ≥ 345 mm square |
| Input R | ≈ 100–150 Ω (feed dependent) | match with a λ/4 taper/strap |
| Beamwidth | HPBW ≈ 61–70/[(C/λ)√(L/λ)]° (measured constants) | ≈ 35–40° for 10 turns |
| Handedness | right-hand screw → RHCP along axis | reverse for LHCP |
| Normal-mode CP | C = √(2Sλ) | rarely practical |

## Worked examples

**Example 1 — 435 MHz rocket-tracking helix.** Target RHCP ≈ 12 dBic with a manageable length. Choose C = 1.12λ = 772 mm (D = 246 mm), α = 12.8° → S = 0.254λ = 176 mm, N = 8 → L = 1.41 m (2.03λ). Emerson: G_max(2.03λ) = 10.25 + 2.48 − 0.30 = **12.4 dBic**; King & Wong (N = 8, C/λ = 1.12): ≈ 12.6 dBic; Kraus would claim 15.8. Ground: 0.4 × 0.4 m aluminium plate or mesh. Feed: the first quarter turn is run close (few mm) to the ground plane and flattened into a strip, forming a tapered microstrip transformer from ≈ 140 Ω to 50 Ω (the King & Wong helices used a 4.7-in linear-taper microstrip transformer [2]); tune by bending the strap height while watching S11. HPBW ≈ 65/(1.12·√2.03) ≈ 41°.

**Example 2 — 2.45 GHz helix for a Wi-Fi/video link.** C = 1.15λ = 141 mm (D = 44.8 mm), S = 0.25λ = 30.6 mm, N = 12 → L = 367 mm (3.0λ): Emerson **13.3 dBic**, KW ≈ 14.8 dBic (α = 12.3°), Kraus 17.4. Ground: 70 × 70 mm cup. Many online "2.4 GHz helix = 17 dBi" claims are Kraus-formula artefacts.

**Example 3 — Why not an axial helix on the rocket?** A 435 MHz axial helix is ≈ 25 cm in diameter — larger than most airframes — and points along the airframe axis, where the ground station usually is *not* (see [antennas-on-rockets](antennas-on-rockets.md)). On the rocket, prefer omnidirectional-in-roll antennas; put the helix on the ground.

**Example 4 — CP ground antenna vs a linear Yagi for a rolling rocket.** With a linear rocket antenna rolling at 5 rev/s, a linear ground Yagi sees two deep polarization nulls per revolution (10 per second); a CP ground antenna sees a constant −3 dB polarization loss (`tools/verify/ant_polarization.py`). An 8-turn helix (12.4 dBic) therefore delivers a steady ≈ 9.4 dB effective gain toward a linear source — similar to a 3-element Yagi's peak but without the fades.

## Practical notes
- **Wind it on a non-conducting former** (PVC tube, foam, spacers); keep metal supports out of the helix. A central *metal* boom along the axis is tolerable for axial-mode helices if small in diameter (King & Wong used a 1.125-in aluminium tube inside the foam) [2].
- **Mechanical rigidity** matters: pitch errors of ±10 % change gain by tenths of a dB but sag or twisting under wind can change more.
- **Weight**: a 1.4 m, 435 MHz helix on a tripod is a two-person item; for portable tracking a crossed Yagi or a short (5-turn) helix is lighter.
- **Phase centre** is ≈ L/4 from the feed (King & Wong rotated the helix about this point for pattern measurements [2]) — important for dish feeds.
- **Dish feeds**: short helices (3–5 turns) are good CP feeds for f/D ≈ 0.4–0.5 dishes; remember reflection flips handedness — wind the feed LHCP to receive an RHCP signal with a prime-focus dish ([horn-reflector-aperture-antennas](horn-reflector-aperture-antennas.md)).

## Common mistakes & misconceptions
- **"Helix gain = 15(C/λ)²NS/λ."** It overestimates by 3–5 dB (King & Wong; Emerson; our MoM).
- **"More turns always = proportionally more gain."** Doubling N adds < 3 dB and the peak-gain frequency drops toward C/λ ≈ 1.07.
- **"The ground plane doesn't matter for a travelling-wave antenna."** A λ/2 square is needed for full performance; radial ground planes cost ≈ 3.5 dB (Emerson).
- **"Any helix is circularly polarized."** Normal-mode helices are essentially linear; axial mode needs C ≈ λ.
- **"RHCP means clockwise as I look at the antenna."** IEEE handedness is defined looking *along* the propagation direction; wound like a right-handed screw (advancing away from the ground) → RHCP ([polarization](antenna-polarization-and-circular-polarization.md)).
- **"A helix is 50 Ω."** 100–150 Ω typically; it needs a matching section.

## How to simulate / verify
- `python3 tools/verify/ant_helix.py` — Kraus vs King & Wong vs Emerson tables and design examples.
- `python3 tools/verify/ant_mom_general.py` — MoM helix over PEC ground (`helix_over_ground()`), returning Z_in and RHCP/LHCP directivity; vary `seg_per_turn` to check convergence (12 → 24 moves gain by 0.3 dB).
- NEC-2: use GH (helix) cards, ≥ 12–16 segments per turn, a real finite ground (wire grid) or a patch surface; check the average gain test ([simulation](antenna-simulation-nec-openems.md)).
- Measure gain by comparison with a known antenna, using a CP source *or* two orthogonal linear measurements; measure AR by rotating a linear source antenna ([antenna measurement](antenna-measurement.md)).

## Open questions / gaps
- QFH design dimensions (loop lengths, H/D ratio) were not verified numerically here; the Kilgus papers and the Coppens calculator should be reviewed and a MoM model added (the general solver supports it).
- Our helix MoM uses an infinite PEC ground; a finite-ground model would quantify Emerson's λ/2-square claim.

## Sources
1. J. D. Kraus, "Helical beam antennas," *Electronics* 20, pp. 109–111, 1947; J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002, ch. 8 (helical antennas: axial and normal modes, G = 15(C/λ)²NS/λ, HPBW = 52/…, R ≈ 140 C/λ, normal-mode AR = 2Sλ/C²). (textbook)
2. H. E. King and J. L. Wong, "Characteristics of 1 to 8 wavelength uniform helical antennas," *IEEE Trans. Antennas Propag.*, vol. AP-28, no. 2, pp. 291–296, Mar. 1980 — measured gain factors 4.2–7.7 (vs 15), HPBW factor 61–70 (vs 52), G·HPBW² = 24 000–31 500, peak at C/λ ≈ 1.07–1.16, empirical peak-gain formula, cavity backing, taper transformer, phase centre ≈ L/4. https://astro.abhinav.ac.in/Literature/Antennae/king&wong_antenna%20characteristics.pdf (peer-reviewed; formula exponents cross-checked against a second source)
3. D. T. Emerson, "The gain of the axial-mode helix antenna," *ARRL Antenna Compendium* vol. 4, pp. 64–68, 1995 — NEC-2 study of ~10 000 helices; Kraus optimistic by up to 4–5 dB; G_max and R_opt fits; ground-plane effects. https://www.cv.nrao.edu/~demerson/cs/helix.htm (peer-level technical paper)
4. C. C. Kilgus, "Resonant quadrifilar helix," *IEEE Trans. Antennas Propag.* AP-17, pp. 349–351, 1969; "Shaped-conical radiation pattern performance of the backfire quadrifilar helix," AP-23, pp. 392–397, 1975. (peer-reviewed; cited, not read in full)
5. Amateur QFH build notes (RadioNugget, 137 MHz; Coppens QFH calculator) — self-phasing via unequal loops, infinite balun, winding direction for RHCP. https://radionugget.com/en/blog/qfh (hobbyist — practice only)
6. u-blox UBX-15030289, *GNSS antennas* app note, §3.2, §4.1, §5.2 — helix vs patch trade-offs, dielectric-loaded helices, ground plane can add 2–3 dB. (app note)
7. L. B. Cebik, "Axial-mode helical antennas" parts 1–2 (antenna2.github.io/cebik) — practice notes. (expert articles)
8. This repository: `tools/verify/ant_helix.py`, `tools/verify/ant_mom_general.py`. (verification)
