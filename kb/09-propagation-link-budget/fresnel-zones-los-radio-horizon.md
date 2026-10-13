---
title: Fresnel zones, line of sight, earth curvature and the radio horizon
domain: 09-propagation-link-budget
slug: fresnel-zones-los-radio-horizon
tags: [fresnel-zone, line-of-sight, 60-percent-clearance, radio-horizon, k-factor, effective-earth-radius, refraction, ducting, earth-bulge, rocket-descent]
prerequisites: [friis-free-space-path-loss.md, ../02-electromagnetics/wave-equation-plane-waves-polarization.md]
related: [diffraction-knife-edge.md, two-ray-ground-reflection.md, empirical-path-loss-models.md, link-budget-methodology.md, ../15-lora-ism-radios/ground-station-design.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Fresnel zones, line of sight, earth curvature and the radio horizon

## Questions this page answers
- What is a Fresnel zone, and why does "I can see the other antenna" not guarantee a free-space link?
- How big is the first Fresnel zone on a 433 MHz or 915 MHz link?
- What is the "60 % clearance" rule and where does it come from?
- How far is the radio horizon, and what is the 4/3-earth (k-factor) model?
- At what altitude will my descending rocket drop below the horizon or below Fresnel clearance?
- How high must my ground-level LoRa antennas be for a clear path?
- What are super-refraction and ducting, and do they matter in Singapore?
- Why is the VHF/UHF radio horizon farther than the visual horizon?

## TL;DR
- The **n-th Fresnel zone** is the set of points where the detour path is longer than the direct path by $n\lambda/2$. Its radius at distances $d_1, d_2$ from the ends: $r_n = \sqrt{n\lambda d_1d_2/(d_1+d_2)}$; practical (ITU-R P.526): $R_n = 550\sqrt{n\,d_1d_2/((d_1+d_2)f_\text{MHz})}$ m with $d$ in km.
- Mid-path $R_1$: **433 MHz: 13 m (1 km), 29 m (5 km), 72 m (30 km); 915 MHz: 9, 20, 50 m** (`tools/verify/prop_fresnel_horizon.py`). The exact ellipsoid and the paraxial formula agree to < 0.1 %.
- **60 % rule:** if every obstacle is at least $0.6R_1$ below the direct ray, the obstacle loss is ≈ 0 dB (knife-edge parameter $v \le -0.85$). Less clearance ⇒ diffraction loss up to 6 dB at grazing and more when blocked ([diffraction-knife-edge](diffraction-knife-edge.md)).
- **Radio horizon** with standard refraction ($k$ = 4/3): $d \approx 4.12\sqrt{h}$ km (h in m); two terminals: $4.12(\sqrt{h_1}+\sqrt{h_2})$. 3 m mast → 7.1 km; 30 m → 22.6 km; rocket at 3 km → 226 km; at 30 km → 714 km.
- **Rocket descent (smooth earth, k = 4/3):** with a 2 m ground mast, geometric LOS is lost only below 12 m altitude at 20 km ground distance, 34 m at 30 km, 115 m at 50 km — but 60 % Fresnel clearance at 433 MHz is lost below ≈ 640 m (20 km), ≈ 980 m (30 km). Below that, the link transitions to the plane-earth/diffraction regime and the last minutes of descent lose ~10–40 dB. Trees and terrain make it earlier.
- **Ground-level LoRa:** a clear 5 km path at 915 MHz needs both antennas ≈ 12.5 m above flat terrain (0.6 R₁ + earth bulge); at 433 MHz ≈ 18 m. With antennas at 2 m you are deep in the 40 dB/decade regime.

## Intuition (no math)
Radio energy does not travel along a pencil-thin ray. By Huygens' principle, every point on a wavefront re-radiates, and the field at the receiver is the sum of contributions from all those points. Contributions from points close to the straight line arrive nearly in phase; those farther out arrive with extra path length and hence extra phase. Group the wavefront into rings where the extra path is 0–½λ, ½–1λ, 1–1½λ…: those are the **Fresnel zones**. The first zone contributes the bulk of the received power; successive zones alternately add and subtract, mostly cancelling.

So the link "needs" a fat, cigar-shaped (ellipsoidal) volume around the line of sight, widest in the middle. At 433 MHz over 5 km that cigar is ~60 m across in the middle. A hill, a building or a tree canopy poking into it removes part of the first zone's contribution even if you can still see the far antenna. That is why "visual line of sight" links often underperform free-space predictions.

The Earth also bulges up into the path, and the atmosphere bends radio waves slightly downward (air is denser, with higher refractive index, near the ground). The bending makes the Earth appear flatter than it is — as if its radius were about 4/3 larger — and extends the radio horizon ~15 % beyond the geometric horizon.

## The math

### Level 1 — formulas
- Fresnel ellipsoid condition: $|TP| + |PR| - |TR| = n\lambda/2$.
- Radius at a point dividing the path into $d_1, d_2$ ($r \ll d_1, d_2$): $r_n = \sqrt{\dfrac{n\lambda d_1d_2}{d_1+d_2}}$; mid-path first zone $r_1 = \tfrac12\sqrt{\lambda d}$.
- ITU-R P.526 practical form: $R_n = 550\sqrt{\dfrac{n\,d_1d_2}{(d_1+d_2)\,f}}$ (m; $d$ km; $f$ MHz) [1].
- Clearance parameter: $v = \sqrt{2}\,h/R_1$ ($h$ = obstacle height above the ray, negative if below) — the knife-edge parameter.
- Effective earth radius $a_e = kR_E$, $R_E$ = 6371 km, standard $k = 4/3$ ($a_e \approx$ 8495 km).
- Horizon distance from height $h$: $d_h = \sqrt{2a_eh + h^2} \approx \sqrt{2a_eh}$ ⇒ **3.57√h km** ($k$ = 1), **4.12√h km** ($k$ = 4/3), $h$ in m.
- Earth bulge at $d_1, d_2$: $h_b = \dfrac{d_1d_2}{2a_e}$ (m, with $d$ in m).

### Level 2 — derivations
**Fresnel radius.** Place the terminals at distance $d_1$ and $d_2$ from a transverse plane; a point in that plane at radius $r$ has path $\sqrt{d_1^2+r^2} + \sqrt{d_2^2+r^2} \approx d_1 + d_2 + \frac{r^2}{2}\left(\frac1{d_1} + \frac1{d_2}\right)$ for $r \ll d$. Setting the excess to $n\lambda/2$ gives $r_n^2 = n\lambda\frac{d_1d_2}{d_1+d_2}$. The script solves the exact ellipsoid equation numerically: at 433 MHz over 1 km the exact $R_1$ is 13.16 m vs 13.15 m paraxial (ITU's rounded 550 constant gives 13.21 m).

**Why 60 %.** Using the knife-edge model, an obstacle whose tip sits a distance $h$ below the ray has $v = \sqrt2 h/R_1$. For $h = -0.6R_1$, $v = -0.85$, where the exact Fresnel–Kirchhoff loss $J(v)$ has recovered to about 0 dB (it oscillates between −1.4 and +1.1 dB for $v < -0.78$; see `prop_knife_edge.py`). With zero clearance (grazing, $v = 0$) the loss is 6.02 dB; the field is exactly half the free-space field because half the wavefront is blocked. The 60 % criterion (also stated in ITU-R P.526 as the edge of the "diffraction zone" [1]) is therefore "clearance at which the obstacle stops mattering", not a physical boundary.

**Refraction and the k-factor.** Radio refractivity $N = (n-1)\times10^6$ at the surface is ≈ 300–400 N-units and usually decreases with height (standard gradient ≈ −40 N/km). A ray in a medium with vertical gradient $dn/dh$ curves with radius $\rho = -1/(dn/dh)$. Relative to the Earth's curvature $1/R_E$, the ray looks straight over an Earth of radius $a_e = kR_E$ with
$$k = \frac{1}{1 + R_E\,dn/dh} = \frac{1}{1 + 6371\cdot(dN/dh)\times10^{-6}}\quad(dN/dh\ \text{in N/km}).$$
$dN/dh = -40$ N/km gives $k = 1.34 \approx 4/3$; 0 N/km gives $k$ = 1 (no bending); **−157 N/km gives $k = \infty$** (rays follow the Earth: the ducting threshold); positive gradients give $k < 1$ (sub-refraction, shortened horizon). ITU-R P.453 gives the statistics of $N$ and $dN/dh$ worldwide [2].

**Horizon.** From right-triangle geometry on a sphere of radius $a_e$: $(a_e + h)^2 = a_e^2 + d_h^2$ ⇒ $d_h = \sqrt{2a_eh + h^2}$. The script shows the approximation is < 0.1 % in error up to 30 km altitude (714.6 km exact vs 713.9 km). The optical horizon is slightly shorter than the radio horizon because optical refraction is weaker ($k$ ≈ 1.15–1.2 for light).

### Level 3 — combining Fresnel clearance with curvature; limits
**Clearance over a smooth earth.** With a straight ray from $(0, h_g)$ to $(D, h_r)$, the clearance at $x$ is $h_g + (h_r - h_g)x/D - x(D-x)/2a_e$, and the requirement is ≥ $0.6\sqrt{\lambda x(D-x)/D}$ everywhere. The script scans rocket altitude $h_r$ to find where this first holds (table below). Over **smooth** earth, losing Fresnel clearance means entering the regime where the ground-reflected ray cancels the direct one (two-ray, 40 dB/decade) and then smooth-earth diffraction beyond the horizon (ITU-R P.526 §3) — the loss grows smoothly, it does not cliff at the 60 % point.

**Irregular terrain.** Real paths need a terrain profile (e.g. SRTM 30 m DEM) with clutter heights (trees 10–30 m, buildings). Tools: Longley–Rice/ITM, ITU-R P.1812/P.452, Radio Mobile, SPLAT!, or a Python profile + P.526 knife-edge calculation ([empirical-path-loss-models](empirical-path-loss-models.md), [diffraction-knife-edge](diffraction-knife-edge.md)).

**Anomalous propagation.** Super-refraction and ducts (strong negative $dN/dh$ from temperature inversions or evaporation over warm sea) trap VHF/UHF/microwave energy and produce links far beyond the horizon — and deep fades on normally good paths. They are common in the tropics and over water (relevant for Singapore and coastal launch sites); ITU-R P.453/P.452 give statistics. For a rocket at kilometres of altitude the path is mostly above the surface layers where ducts form, so ducting mainly affects the final descent and the landed case.

**Validity.** The paraxial Fresnel formula needs $r \ll d_1, d_2$ (fails within a few wavelengths of an antenna); the zone concept assumes the antennas' patterns are broad compared with the zone angular size.

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $R_1 = 550\sqrt{d_1d_2/((d_1+d_2)f)}$ m | km, MHz | 433 MHz mid-path: 13 m @1 km, 29 m @5 km, 72 m @30 km |
| $0.6R_1$ clearance ⇒ ~0 dB obstacle loss | single obstacle | 915 MHz 5 km: 12.1 m |
| $d_h = 4.12\sqrt{h}$ km | k = 4/3 | 2 m: 5.8 km; 5 m: 9.2 km; 20 m: 18.4 km |
| $d_\text{LOS} = 4.12(\sqrt{h_1} + \sqrt{h_2})$ km | smooth earth | rocket 1 km + mast 3 m: 137 km |
| $h_b = d_1d_2/(2a_e)$ | | 5 km mid: 0.37 m; 20 km: 5.9 m |
| $k = 1/(1 + 6.371\times10^{-3}\,dN/dh)$ | dN/dh in N/km | −40 → 1.34; −157 → ∞ (duct) |
| Ground clearance needed (equal heights, midpoint) ≈ $h_b + 0.6R_1$ | flat terrain | 915 MHz: 5.4 m (1 km), 12.5 m (5 km), 18.6 m (10 km) |

## Worked examples
**1 — First Fresnel zone of the 30 km rocket link.** 433.125 MHz, rocket at 30 km slant range: $R_1$ mid-path = 72 m; but near the ground station, 100 m from the mast, $R_1$ = 8.3 m and 10 m away 2.6 m. For an elevated rocket the ray climbs away from the ground quickly, so only obstacles near the ground station matter: a 5 m bush 50 m in front of a 3 m mast, on a ray rising at 10°, is clear (the ray is 11.8 m up at 50 m, $R_1$ ≈ 5.9 m).

**2 — When does a descending rocket lose the link? (smooth earth, k = 4/3)**

| GS mast | Ground distance | LOS lost below | 0.6 R₁ lost below (433 MHz) | (915 MHz) |
|---|---|---|---|---|
| 2 m | 5 km | 0 m (always LOS) | 158 m | 76 m |
| 2 m | 10 km | 1 m | 316 m | 154 m |
| 2 m | 20 km | 12 m | 636 m | 318 m |
| 2 m | 30 km | 34 m | 982 m | 494 m |
| 2 m | 50 km | 115 m | 1578 m | 884 m |
| 5 m | 20 km | 7 m | 274 m | 142 m |
| 5 m | 30 km | 25 m | 426 m | 230 m |
| 20 m | 30 km | 8 m | 138 m | 84 m |
| 20 m | 50 km | 59 m | 288 m | 196 m |

Raising the ground antenna from 2 m to 20 m moves the "Fresnel-clear" altitude from ~1 km down to ~140 m at 30 km — this is why a hilltop or a mast is worth more than any amount of transmit power for tracking the final descent. Beyond these points the loss increases progressively (two-ray regime, then diffraction) rather than stopping the link immediately.

**3 — Ground-level LoRa (both ends on the ground).** For a 5 km, 915 MHz link over flat ground, the midpoint needs 0.37 m (bulge) + 12.1 m (0.6 R₁) ≈ **12.5 m** of antenna height at both ends to behave like free space; at 433 MHz ≈ 18 m. With 2 m antennas you are far inside the first zone: the link is in the plane-earth regime (−127 dB at 3 km for 2 m/2 m, vs FSPL −101 dB at 915 MHz; `prop_empirical.py`). This is the physics behind Meshtastic users' observation that mountaintop nodes achieve hundreds of km while ground-level nodes manage a few km.

**4 — Elevation angles (curvature included).** A rocket at 3 km altitude and 30 km ground distance is at 5.6° elevation (slant 30.15 km); at 10 km altitude, 18.3°; at 1 km altitude and 30 km, 1.8° — low enough that ground-reflection lobing and terrain matter ([two-ray-ground-reflection](two-ray-ground-reflection.md)).

## Practical notes
- **Survey the horizon at the ground station:** with a phone inclinometer or an online horizon tool (e.g. HeyWhatsThat), record the horizon elevation in the landing-zone direction; any terrain above 0.5–1° elevation will shadow the final descent at 20–30 km.
- **Trees count as terrain** at UHF (and add vegetation loss); use canopy height, not ground height.
- **Put the mast where the Fresnel zone is narrow** — near your own end the zone is small, so a few metres of height clear nearby obstacles.
- **For recovery,** a second receiver closer to the predicted landing area (or a drone relay) is usually more effective than increasing transmit power.

- **Quick answer — radio vs visual horizon.** The atmosphere refracts radio waves slightly. Refractivity falls with height, by about −40 N/km in the standard atmosphere, so rays curve gently toward the Earth. That is equivalent to a larger Earth of radius $ka$, $k$ = 4/3. The radio horizon is therefore $\sqrt{4/3}$ ≈ **1.15× (≈ 15 % farther than)** the geometric horizon: 4.12√h km vs 3.57√h km (h in m). The visual horizon is only slightly extended (k ≈ 1.15–1.2 for light), because water vapour, the dominant variable in radio refractivity, barely affects optical refraction. Ducting, super-refraction, sporadic-E and the other "beyond-horizon" VHF/UHF modes are in [VHF/UHF anomalous propagation](vhf-uhf-anomalous-propagation.md).

## Common mistakes & misconceptions
- **"I can see it, so it's free space."** Visual LOS is not Fresnel clearance.
- **Requiring 100 % first-zone clearance.** 60 % is enough for ~0 dB obstacle loss; beyond that, the returns diminish.
- **Using the geometric horizon (3.57√h)** for radio; the standard-refraction value is 4.12√h — unless you are designing for worst-case sub-refraction (k ≈ 2/3 in some ITU-R P.530 planning rules for fixed links).
- **Thinking the Fresnel zone is widest near the antennas.** It is widest at mid-path and shrinks to zero at the ends.
- **Treating "loss of 0.6 R₁ clearance" as loss of the link.** It marks the start of excess loss, which then grows gradually.

## How to simulate / verify
- `tools/verify/prop_fresnel_horizon.py` — exact vs paraxial Fresnel radius, ITU form, horizons (exact vs approx, k = 1 and 4/3), earth bulge, antenna heights for ground-level clearance, rocket descent altitudes for LOS and 0.6 R₁ clearance, elevation angles with curvature.
- For real terrain: download SRTM tiles, extract the profile between GS and landing point, and apply P.526 knife-edge / Deygout (`prop_knife_edge.py`) to the profile; or use Radio Mobile / SPLAT! (ITM).

## Open questions / gaps
- Refractivity-gradient statistics for Singapore and Marcus's launch sites (ITU-R P.453 maps) not extracted; ducting probability is qualitative here.
- The descent table assumes smooth earth; site-specific DEM analysis for real launch sites is future work (domain 20).

## Sources
1. ITU-R Recommendation P.526-14 (01/2018), *Propagation by diffraction*, §2.1 (Fresnel ellipsoids, eqs. 1–3), §2.3 (diffraction zone, 60 % of R₁), §4.1 (knife edge). https://www.itu.int/rec/R-REC-P.526/en (standard)
2. ITU-R Recommendation P.453, *The radio refractive index: its formula and refractivity data* (current revision). https://www.itu.int/rec/R-REC-P.453/en (standard) — N, dN/dh statistics, k-factor, ducting (cited for definitions; data not extracted).
3. J. S. Seybold, *Introduction to RF Propagation*, Wiley 2005, ch. 3 (Fresnel zones, earth curvature, k-factor, horizon). (textbook)
4. S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., Wiley 2007, ch. 5–6 (Fresnel zones, clearance, refraction). (textbook)
5. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, §4.7 (diffraction, Fresnel zone geometry). (textbook)
6. Meshtastic documentation, "Range tests" (331 km mountain-to-mountain record, SF12/BW62.5; 206 km balloon). https://meshtastic.org/docs/overview/range-tests/ (community docs — anecdotal)
7. `tools/verify/prop_fresnel_horizon.py`, `tools/verify/prop_knife_edge.py` (this KB).
