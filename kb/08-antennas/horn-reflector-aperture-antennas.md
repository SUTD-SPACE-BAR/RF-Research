---
title: Horn, reflector and aperture antennas — aperture efficiency, optimum pyramidal horn, parabolic dish gain, taper vs spillover, feeds
domain: 08-antennas
slug: horn-reflector-aperture-antennas
tags: [aperture-antenna, aperture-efficiency, horn, pyramidal-horn, standard-gain-horn, parabolic-reflector, dish, illumination-taper, spillover, feed, f-over-d, ruze, cantenna, waveguide]
prerequisites: [antenna-fundamentals.md, ../02-electromagnetics/waveguides-and-cavity-resonators.md, ../00-math-foundations/fourier-series-and-transform.md]
related: [helical-antennas.md, patch-antennas.md, antenna-measurement.md, ../12-phased-arrays/tapering-sidelobe-control.md, ../11-radar/radar-range-equation.md, lens-and-reflectarray-antennas.md, slot-antennas.md]
level: mixed
confidence: high
last_updated: 2026-10-13
---

# Horn, reflector and aperture antennas

## Questions this page answers
- Why is the gain of a big aperture antenna ≈ 4πA/λ² times an efficiency?
- What is aperture efficiency, and why is a dish only 55–70 % efficient?
- How do I design an optimum-gain pyramidal horn for 5.8 or 10 GHz?
- How much gain does a 1.2 m dish give at 2.45 or 5.8 GHz?
- What is the trade-off between illumination taper and spillover, and what edge taper is optimum?
- How do f/D and the feed pattern go together?
- How big must a "cantenna" (circular waveguide feed) be for 2.4 GHz?
- How much does surface roughness of a dish cost (Ruze)?
- Why does a prime-focus dish reverse circular polarization?
- What are waveguide irises and cross-shaped irises, how does a horn polariser make circular polarisation, and how is a patch antenna trimmed after etching?

## TL;DR
- Any aperture antenna has D = e_ap·4πA/λ². A **uniformly illuminated, in-phase** aperture gives e_ap = 1 (our numerical integration: 6 × 6λ → 26.68 dBi vs 4πA/λ² = 26.56 dBi; small apertures slightly exceed it because of the element (obliquity) pattern) — `tools/verify/ant_aperture.py`.
- **Optimum pyramidal horn**: aperture efficiency ≈ **0.51** (script 0.512), from the quadratic phase errors allowed at the optimum (s = 1/4 in the E-plane, t = 3/8 in the H-plane) and the cosine H-plane taper. Example: 15 dBi at 5.8 GHz from WR-159 → 132.8 × 98.9 mm aperture, 64 mm long (Balanis design procedure [1]).
- **Parabolic dish**: G = η(πD/λ)². With a cosⁿ-type feed, taper × spillover efficiency peaks at ≈ **0.82–0.85** when the rim illumination (feed pattern + spherical spreading) is ≈ **−10 to −12 dB** (script, f/D 0.3–0.6). Real dishes reach η ≈ 0.55–0.70 after blockage, cross-polar, phase-centre, surface and feed losses.
- **1.2 m dish, η = 0.6**: 27.6 dBi at 2.45 GHz, 35.0 dBi at 5.8 GHz; HPBW ≈ 70λ/D = 7.1° and 3.0°.
- **Ruze**: surface rms error ε costs exp[−(4πε/λ)²]: ε = λ/32 → −0.67 dB, λ/16 → −2.7 dB.
- A single reflection reverses CP sense: the feed of a prime-focus dish must be the *opposite* handedness of the signal ([polarization](antenna-polarization-and-circular-polarization.md)).

## Intuition (no math)
A large antenna is like a window: the fields across its mouth ("aperture") determine the far field through a 2-D Fourier transform. A wide window with a uniform, in-phase field sends a narrow beam straight ahead (beamwidth ≈ λ/D radians). Anything that makes the aperture field non-uniform (tapering toward the edges), out of phase (a horn's curved wavefront), or spill past the edge (a dish feed illuminating beyond the rim) reduces gain below 4πA/λ² — that is the aperture efficiency.

For a dish there is a tug-of-war: illuminate the rim strongly and you use the whole area uniformly but spill a lot of feed power past the edge (wasted, and it looks at the warm ground behind the dish); illuminate the rim weakly and nothing spills, but the outer part of the dish is barely used. The best compromise puts the rim about 10 dB below the centre.

A horn is a waveguide flared so the wave expands smoothly into free space. Flare it too quickly and the wavefront at the mouth is strongly curved (phase error); flare it too slowly and the horn is very long. The "optimum horn" allows just enough phase error to maximise gain for a given length.

## The math

### Level 1 — equations
- Aperture directivity: D = e_ap(4π/λ²)A_phys; e_ap = e_taper·e_spill·e_phase·e_block·e_surface·e_xpol…
- Dish: G = η(πD/λ)² (D = diameter); HPBW ≈ 65–72 λ/D degrees (depends on taper; 70λ/D used here).
- f/D and rim half-angle: θ₀ = 2 arctan[1/(4 f/D)].
- Ruze: η_surface = exp[−(4πε/λ)²], ε = rms normal surface error.
- Optimum pyramidal horn (Balanis §13.4 [1]): A = √(3λρ_h) (H-plane aperture), B = √(2λρ_e) (E-plane); design by solving
$$\big(\sqrt{2\chi}-\tfrac{b}{\lambda}\big)^2(2\chi-1)=\Big(\tfrac{G}{2\pi}\sqrt{\tfrac{3}{2\pi}}\tfrac{1}{\sqrt\chi}-\tfrac{a}{\lambda}\Big)^2\Big(\tfrac{G^2}{6\pi^3}\tfrac1\chi-1\Big),\quad \rho_e=\chi\lambda,\ \rho_h=\frac{G^2}{8\pi^3\chi}\lambda,$$
  with a × b the feeding waveguide; the E- and H-plane horn lengths p_e and p_h must come out equal (a physical-realisability check the script prints).
- Circular waveguide (cantenna) TE₁₁ cut-off f_c = 1.8412c/(2πa); guide wavelength λ_g = λ₀/√(1 − (f_c/f)²); TM₀₁ cut-off 2.4049c/(2πa).

### Level 2 — aperture theory
For an aperture field E_a(x′, y′) (equivalence principle: magnetic plus electric surface currents — a "Huygens source"), the far field is proportional to its 2-D Fourier transform, times an obliquity factor (1 + cosθ)/2:
$$\mathbf E(\theta,\phi)\propto\frac{1+\cos\theta}{2}\iint E_a(x',y')\,e^{jk\sin\theta(x'\cos\phi+y'\sin\phi)}dx'dy'.$$
On axis, the field is ∝ ∫∫E_a, while the total radiated power is ∝ ∫∫|E_a|² (Parseval), so by the Cauchy–Schwarz inequality
$$e_\text{taper}=\frac{\big|\iint E_a\,dA\big|^2}{A\iint|E_a|^2dA}\le 1,$$
with equality only for uniform amplitude and phase. A cos(πx/a) taper in one plane (TE₁₀ H-plane) gives e_taper = 8/π² = 0.81.

**Dish with a feed pattern G_f(θ′).** Silver's formulation [1], [2]: the aperture efficiency of a paraboloid illuminated by a feed with power pattern G_f is
$$e_\text{ap}=\cot^2\frac{\theta_0}{2}\left|\int_0^{\theta_0}\sqrt{G_f(\theta')}\tan\frac{\theta'}{2}\,d\theta'\right|^2,$$
and the spillover efficiency is the fraction of feed power inside θ₀. With G_f = 2(2q+1)cos^{2q}θ′ (a common model), our script finds, for each f/D, the q maximising e_ap:

| f/D | rim half-angle | best q | taper eff. | spillover eff. | aperture eff. | edge illumination |
|---|---|---|---|---|---|---|
| 0.3 | 79.6° | 0.5 | 0.874 | 0.967 | 0.845 | −12.0 dB |
| 0.4 | 64.0° | 1.0 | 0.903 | 0.916 | 0.827 | −10.0 dB |
| 0.5 | 53.1° | 2.0 | 0.889 | 0.922 | 0.820 | −10.8 dB |
| 0.6 | 45.2° | 3.0 | 0.893 | 0.914 | 0.817 | −10.5 dB |

(Edge illumination = feed pattern at the rim plus the cos²(θ₀/2) spherical-spreading term.) This reproduces the classic rule that ≈ −10 to −12 dB edge illumination maximises gain at ≈ 0.8 taper×spillover efficiency (Balanis ch. 15 [1]; Kraus [2]).

### Level 3 — horns in detail, and other losses
- **Horn phase error.** For a flare of slant length ρ and aperture half-width a/2, the edge phase lag is ≈ π(a/2)²/(λρ) → parameters s = B²/(8λρ_e) and t = A²/(8λρ_h). Gain vs flare peaks at s ≈ 1/4 (E-plane) and t ≈ 3/8 (H-plane); substituting gives the A = √(3λρ_h), B = √(2λρ_e) conditions and e_ap ≈ 0.51 [1]. Standard-gain horns used as gain references are built to these dimensions and their gain is calculable to ≈ ±0.3 dB.
- **Conical and corrugated horns** give nearly symmetric patterns and low cross-polarization (corrugated: hybrid HE₁₁ mode, ≈ −10 dB edge taper naturally) — preferred dish feeds.
- **Blockage**: a feed/subreflector of diameter d_b removes a fraction x = (d_b/D)² of a uniformly illuminated aperture; the on-axis field drops by (1 − x), so the gain factor is ≈ (1 − x)² ≈ 1 − 2x for small blockage (e.g. d_b/D = 0.1 → −0.09 dB; 0.2 → −0.36 dB). Tapered illumination makes central blockage relatively worse. Offset dishes avoid it.
- **Phase-centre defocus**: the feed's phase centre must be at the focus to within ~λ/10 axially for small loss.
- **Surface error**: Ruze exp[−(4πε/λ)²]: a TV dish (ε ~ 0.5–1 mm) is fine at 2.45 GHz (λ/32 ≈ 3.8 mm tolerance) and marginal at 24 GHz.

## Feeds for amateur dishes (1–10 GHz)

| Feed | Band use | Pattern / notes |
|---|---|---|
| Open waveguide / "cantenna" (circular TE₁₁) | 2.4, 5.8 GHz | broad beam suits f/D ≈ 0.35–0.45; mount so phase centre is at focus |
| Short axial helix (3–5 turns) | 1.2–2.5 GHz, CP | wind LHCP to receive RHCP with a prime-focus dish |
| Patch / dual patch | 1.2–5.8 GHz | broad beam, suits deep dishes (low f/D) |
| Dipole + reflector disc ("splash plate") | 0.4–2.4 GHz | simple; moderate efficiency |
| Septum polarizer horn | CP, 2.4/10 GHz | excellent CP, dual sense |
| Scalar-ring ("W2IMU", Kumar) horns | microwave | shaped for specific f/D |

**Cantenna numbers (circular TE₁₁)**: for 2.45 GHz the diameter must exceed 71.7 mm (f_c = 2.45 GHz); a 90 mm can has f_c = 1.95 GHz (TM₀₁ at 2.55 GHz stays cut off at 2.45 GHz), λ_g = 202.5 mm, so the probe sits λ_g/4 = 50.6 mm from the closed end, probe length ≈ λ₀/4 ≈ 30.6 mm. A 76 mm can is only just above cut-off (f_c = 2.31 GHz, λ_g = 370 mm) — very dispersive and sensitive; prefer 85–95 mm.

## Irises, polarisers and tuning features
Numbers in this section are checked in `tools/verify/s18_horn_polariser.py`.

**Irises (thin plates with a hole, across a waveguide).**
- *Inductive iris.* A plate that narrows the broad wall (the dimension the E-field is parallel to) acts as a shunt inductance.
- *Capacitive iris.* A plate that narrows the narrow wall puts the gap across the E-field and acts as a shunt capacitance.
- *Resonant iris.* A window that does both is a parallel LC. It is transparent at its resonance and reflective elsewhere, so it is a one-element band-pass filter. These are the coupling elements of waveguide filters and the matching "windows" behind horn feeds [8].
- *Cross-shaped iris.* A cross slot resonates for both polarisations at once, because each arm is a slot resonant when its length is close to λ/2 (Babinet: the slot is the dual of a dipole, see [slot antennas](slot-antennas.md)). At 10.368 GHz that is about 14.5 mm before end and wall corrections. Cross irises are used where a filter or coupling window must pass two orthogonal or circular polarisations equally, for example in dual-polarisation or CP feeds. In a periodic sheet, cross (and Jerusalem-cross) elements form frequency-selective surfaces and dichroic subreflectors [11]. Tune them in a simulator (openEMS) or on the bench: the slot length, the width and the plate thickness all shift the resonance.

**Polarisers (linear to circular, in the feed).**
- *Principle.* All of them do one thing: they split the incoming linear field into two equal components at ±45°, and delay one of them by 90° relative to the other.
- *Ways to get the 90°:*
  - a dielectric vane at 45° in a circular or square guide;
  - rows of screws or pins, which add capacitance and slow one component;
  - an iris-loaded or corrugated section;
  - a guide whose two transverse dimensions differ (differential cut-off, worked below);
  - a meander-line sheet across the horn mouth [10].
- *Septum polariser.* A stepped metal septum in a square guide turns two rectangular ports into the two circular senses at once, RHCP on one port and LHCP on the other. It is the classic dual-sense feed [9] and is listed in the feed table above.
- *Sense.* The sense of circular polarisation depends on which component is delayed. Check it against the IEEE definition ([polarisation page](antenna-polarization-and-circular-polarization.md)), and remember that a prime-focus dish reverses it.

*Worked example — differential-cut-off polariser at 10.368 GHz.*
1. **The guide.** A 20 mm square guide carries a 45° linear wave as two equal TE₁₀/TE₀₁ components. The next higher modes (TE₁₁/TM₁₁) are cut off at 10.60 GHz, just above the operating frequency.
2. **The squeeze.** Narrow one wall to 17 mm for a length L. The component whose cut-off depends on that wall rises from 7.49 to 8.82 GHz cut-off, so it travels with a smaller β, and the two components drift apart in phase.
3. **The length.** 90° of differential phase needs $L = (\pi/2)/(\beta_{20} - \beta_{17})$ = **43.8 mm**.
4. **Bandwidth.** The differential phase is 100.2° at 10.0 GHz and 82.9° at 10.7 GHz, giving an axial ratio of 1.55 dB and 1.08 dB. For equal amplitudes AR = 20 log|tan(Δφ/2)|, so a ±10° phase error costs about 1.5 dB.
5. **Matching.** Abrupt steps reflect, so real designs taper or step the transitions and then retune.

**Patch tuning features (how a printed antenna is trimmed after it is etched).**
- *Length trim.* The resonance scales as $1/L_{eff}$. Trimming the radiating length by ΔL raises the frequency by ≈ $f\,\Delta L/L_{eff}$. On the 2.45 GHz FR-4 patch of the [patch page](patch-antennas.md) ($L_{eff}$ ≈ 30.3 mm), a 0.3 mm trim moves it **+24 MHz**, about 0.4 of its 2.6 % bandwidth. Etch slightly long, measure, then trim. Copper tape extends the length temporarily for tests.
- *Tuning tabs and flags.* Small copper tabs on the radiating edges, or rows of pads along the feed line that can be bridged with solder, add capacitance in steps. The pads beside PA and LNA traces on many RF boards are the same idea applied to a matching network (→ [impedance matching](../03-transmission-lines-matching/impedance-matching-lumped-and-distributed.md)).
- *Feed position.* Moving the inset depth or the probe position sets the match (cos² law), largely independently of the frequency.
- *CP trim.* On a truncated-corner or nearly-square CP patch, trimming one corner or one side moves the split of the two modes. That sets the axial ratio, and it must be checked with a rotating linear probe or two orthogonal measurements.
- *Shorting pins.* Pins and slots lower the resonance (PIFA-like) and are a coarse adjustment.
- *Environment.* Ceramic GNSS patches are pre-tuned for a given ground-plane size, and they shift when a radome or nose cone is fitted over them, so retune in the final enclosure ([GNSS antennas](gnss-antennas.md)).

## Design equations & rules of thumb

| Item | Rule | Example |
|---|---|---|
| Aperture gain | e_ap·4πA/λ² | 0.25 m² at 5.8 GHz, e = 0.6 → 30.3 dBi |
| Dish gain | η(πD/λ)², η 0.55–0.70 | 0.6 m @1.575 GHz → 17.7 dBi |
| HPBW | ≈ 70λ/D (°) | 1.2 m @5.8 GHz → 3.0° |
| Best edge illumination | −10 to −12 dB | taper×spill ≈ 0.82–0.85 |
| Optimum horn e_ap | 0.51 | 15 dBi @5.8 GHz: 133 × 99 mm |
| Horn optimum | A = √(3λρ_h), B = √(2λρ_e) | — |
| Ruze | exp[−(4πε/λ)²] | ε = λ/32 → −0.67 dB |
| Far field (measurement) | 2D²/λ | 1.2 m @5.8 GHz → 56 m |
| CP with prime-focus dish | feed of opposite sense | LHCP feed for RHCP signal |

## Worked examples

**Example 1 — Optimum 15 dBi horn for a 5.8 GHz test link (WR-159, 40.39 × 20.19 mm).** Script: χ solved, aperture 132.8 × 98.9 mm, E- and H-plane lengths p_e = p_h = 64.3 mm (consistent → realisable), e_ap = 0.512. As a check: 0.512 × 4π × 0.1328 × 0.0989/λ² (λ = 51.7 mm) = 31.6 → 15.0 dBi. Build from 1.6 mm FR-4 or brass sheet soldered at the seams; feed with a WR-159-to-SMA adapter or a probe λ_g/4 from a back short.

**Example 2 — 20 dBi horn at 10 GHz (WR-90)**: 134.2 × 104.2 mm aperture, 156.5 mm long, e_ap 0.512 — a classic X-band standard-gain-horn geometry, also useful for 10 GHz Doppler/FMCW radar experiments ([radar](../11-radar/radar-range-equation.md)).

**Example 3 — Would a dish help the rocket ground station?** A 1.2 m dish at 433 MHz is only 1.7λ across: G ≈ 0.6·(π·1.73)² ≈ 17.5 → 12.5 dBi with a ≈ 40° beam — similar to a DL6WU Yagi of 1.7 m boom (14 dBi), but heavier, with more wind load, and needing a feed ≥ λ/2 in size. At 433–915 MHz, Yagis/helices win; dishes pay off from ≈ 2 GHz upward.

**Example 4 — 2.45 GHz video downlink from a rocket to a 0.9 m offset TV dish.** D = 0.9 m, η ≈ 0.55 → G = 0.55·(π·0.9/0.1224)² = 293 → 24.7 dBi; HPBW ≈ 70 × 0.1224/0.9 ≈ 9.5° — requires active tracking (GNSS-fed pointing). The feed must suit the offset dish's effective f/D (≈ 0.6–0.7 for TV offsets) — a patch or a cantenna with a choke ring.

## Practical notes
- Standard-gain horns are the usual *reference antennas* for gain-transfer measurement above ~1 GHz ([antenna measurement](antenna-measurement.md)).
- Measure the feed's phase centre (or take it from simulation) and position it at the focus; small axial errors defocus the beam.
- Wind load scales with area; mesh reflectors (mesh openings < λ/10) cut wind load with little gain loss below ~5 GHz.
- Dish sidelobes and spillover look at the warm ground: for low-noise reception (radio astronomy, weak satellites) prefer slightly more taper (−12 to −15 dB) at a small gain cost.
- Arrays of patches can replace dishes for moderate gain and electronic steering — see [12-phased-arrays](../12-phased-arrays/beam-steering-grating-lobes.md).
- **Offset dishes and LNB feeds** (offset angle, equivalent f/D, re-feeding a TV dish at L band): [06 receivers § LNBs and offset dishes](../06-rf-circuits/receiver-architectures.md#satellite-tv-lnbs-offset-dishes-and-l-band-re-feeds).

## Common mistakes & misconceptions
- **"Gain = 4πA/λ²."** Only for uniform in-phase illumination with no spillover; real dishes 0.55–0.70, horns ≈ 0.5.
- **"Uniform dish illumination is best."** It maximises taper efficiency but spills power; the optimum is −10 to −12 dB at the rim.
- **"A bigger can makes a better cantenna."** Too big allows higher-order modes (TM₀₁ above 2.4049c/2πa); too small is near cut-off and lossy/dispersive.
- **"A dish reflector keeps the polarization sense."** It reverses CP sense.
- **"Feed gain should be as high as possible."** The feed beamwidth must match the dish's rim angle; a high-gain feed under-illuminates.

## How to simulate / verify
- `python3 tools/verify/ant_aperture.py` — uniform-aperture directivity, dish taper/spillover optimisation, horn design, far-field distances.
- openEMS has conical-horn and pyramidal-horn tutorials; reflector antennas are best done with physical-optics tools (e.g., GRASP student edition) or large-scale FDTD/MoM with care.
- Measure horn gain with the three-antenna method (two identical horns + a third) — [antenna measurement](antenna-measurement.md).

## Open questions / gaps
- Blockage loss expression is given in approximate form; a cross-check against Balanis §15 numerical examples is pending.
- Offset-dish feed design (cross-polar, feed tilt optimisation) is not covered in depth. Offset angle and equivalent f/D are now worked in [06 receivers § LNBs and offset dishes](../06-rf-circuits/receiver-architectures.md#satellite-tv-lnbs-offset-dishes-and-l-band-re-feeds).
- Irises/polarisers section (W5-S18): the polariser example ignores step reflections and the iris λ/2 rule ignores wall/thickness corrections; refs [9]–[10] confirmed bibliographically only, [11] cited from knowledge. No openEMS run of a cross iris yet.

## Sources
1. C. A. Balanis, *Antenna Theory*, 4th ed., 2016 — ch. 12 (aperture antennas, Huygens source, uniform/tapered apertures), ch. 13 (horns: E-plane, H-plane, pyramidal, optimum design procedure, e_ap ≈ 0.51), ch. 15 (reflectors: Silver's aperture efficiency, spillover, taper, blockage, Ruze). (textbook)
2. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — aperture efficiency, reflector design. (textbook)
3. S. Silver (ed.), *Microwave Antenna Theory and Design*, MIT Rad. Lab. Series vol. 12, McGraw-Hill, 1949 — paraboloid aperture efficiency. (textbook, historical; cited via Balanis)
4. J. Ruze, "Antenna tolerance theory — a review," *Proc. IEEE* 54(4), pp. 633–640, 1966. (peer-reviewed; cited)
5. S. J. Orfanidis, *Electromagnetic Waves and Antennas*, 2016 ed., ch. 18 "Radiation from Apertures" (equivalence, Huygens source, rectangular/circular apertures) and ch. 21 "Aperture Antennas" (§21.2–21.5 horns, §21.7–21.11 reflectors). [chapter numbers checked against the 2016 edition's table of contents, W5-S18 2026-10-13; the 2010 edition numbers ch. 11–18 one lower, with Aperture Antennas as ch. 18 and Currents on Linear Antennas as ch. 21]. https://eceweb1.rutgers.edu/~orfanidi/ewa/ (textbook)
6. P. Wade (W1GHZ), *The W1GHZ Online Microwave Antenna Book* — practical dish feeds, "Helical feed antennas" (2002). http://www.w1ghz.org/antbook/conf/Helical_feed_antennas.pdf (expert practice)
7. This repository: `tools/verify/ant_aperture.py`. (verification)
8. D. M. Pozar, *Microwave Engineering*, 4th ed., Wiley 2012, §4.6 "Discontinuities and modal analysis" (waveguide irises as shunt susceptances; section title from the Wiley ToC in gaps/D4-curriculum.md §3.1). (textbook)
9. M. H. Chen, G. N. Tsandoulas, "A wide-band square-waveguide array polarizer," *IEEE Trans. Antennas Propag.* 21(3), 389–391, 1973 — first journal paper on the stepped-septum polarizer (≈ 20 % bandwidth per a later review). (peer-reviewed; bibliographic data confirmed by search 2026-10-13, paper not read)
10. L. Young, L. A. Robinson, C. A. Hacking, "Meander-line polarizer," *IEEE Trans. Antennas Propag.* 21(3), 376–378, 1973. (peer-reviewed; bibliographic data confirmed by search 2026-10-13, paper not read)
11. B. A. Munk, *Frequency Selective Surfaces: Theory and Design*, Wiley 2000 — cross and Jerusalem-cross elements. (textbook; bibliographic data checked against Crossref by W5-S18b, 2026-10-13; content cited from knowledge)
12. This repository: `tools/verify/s18_horn_polariser.py` — differential-cut-off polariser length and AR vs frequency, cross-arm λ/2, patch trim. (verification)
