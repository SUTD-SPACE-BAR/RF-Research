---
title: Diffraction — knife-edge, rounded obstacles and multiple edges (Deygout, Epstein–Peterson, Bullington)
domain: 09-propagation-link-budget
slug: diffraction-knife-edge
tags: [diffraction, knife-edge, fresnel-kirchhoff, v-parameter, ITU-R-P.526, fresnel-integrals, deygout, epstein-peterson, bullington, rounded-obstacle, terrain-shadowing, landed-rocket]
prerequisites: [fresnel-zones-los-radio-horizon.md, ../00-math-foundations/special-functions-bessel-sinc.md]
related: [two-ray-ground-reflection.md, empirical-path-loss-models.md, atmospheric-rain-attenuation.md, link-budget-methodology.md, link-margin-availability.md]
level: mixed
confidence: high
last_updated: 2026-09-27
---

# Diffraction — knife-edge, rounded obstacles and multiple edges

## Questions this page answers
- How much signal do I lose when a hill or building blocks the line of sight?
- What is the Fresnel–Kirchhoff parameter $v$, and how do I compute it?
- Why is there 6 dB of loss even when the obstacle just grazes the line of sight?
- How good is the ITU-R P.526 approximation to the exact knife-edge loss?
- How do I handle two or more ridges (Deygout, Epstein–Peterson, Bullington), and why do they disagree?
- My rocket landed behind a ridge — can I still hear it, and does 433 or 915 MHz do better?

## TL;DR
- **Knife-edge parameter:** $v = h\sqrt{\dfrac{2(d_1+d_2)}{\lambda d_1d_2}} = \sqrt2\,\dfrac{h}{R_1}$ ($h$ = height of the edge above the direct line, negative if below; $R_1$ = first Fresnel radius at the edge).
- **Loss** (exact, Fresnel integrals): $J(v) = -20\log_{10}\left|\tfrac{1+j}{2}\int_v^\infty e^{-j\pi t^2/2}dt\right|$ — **6.02 dB at grazing ($v$ = 0)**, 13.9 dB at $v$ = 1, 19.1 dB at 2, 22.5 dB at 3, 33.0 dB at 10; ≈ 0 dB (±1.4 dB ripple) for $v \lesssim -0.8$ (60 % clearance).
- **ITU-R P.526 approximation** $J(v) = 6.9 + 20\log_{10}\left(\sqrt{(v-0.1)^2+1} + v - 0.1\right)$ for $v > -0.78$: max error **0.12 dB** over −0.7 ≤ v ≤ 10 (`tools/verify/prop_knife_edge.py`). Large-$v$ asymptote: $J \approx 13 + 20\log_{10}v$.
- **Frequency dependence:** $v \propto \sqrt f$, so for a deep shadow loss grows ~+10 dB per decade of frequency (≈ 3 dB going 433 → 915 MHz for the same obstacle).
- **Multiple edges:** Deygout (main edge + sub-paths) is usually most pessimistic, Epstein–Peterson (sequential) next, Bullington (single equivalent edge) most optimistic. Example (two ridges, 6 km, 433 MHz): 23.0 / 21.8 / 16.3 dB.
- **Landed rocket 1.5 km behind a 25 m ridge (6 km from GS):** single-edge loss 15.1 dB at 433 MHz, 17.9 dB at 915 MHz — on top of ground-level effects.

## Intuition (no math)
Waves bend around obstacles. By Huygens' principle every point on a wavefront radiates onward; if an obstacle blocks part of the wavefront, the unblocked part still sends energy into the "shadow", just weaker. The deeper you are in the shadow (the more of the first Fresnel zone is blocked), the weaker the field.

At exactly grazing — the obstacle's tip just touching the line of sight — half of the wavefront is blocked. The field is half the unobstructed value: −6 dB. Clear the obstacle by about 60 % of the first Fresnel radius and the loss vanishes. Go deeper into the shadow and the loss grows steadily, roughly 6 dB each time the "shadow depth" (in units of Fresnel radius) doubles.

Because the Fresnel radius shrinks as frequency rises, the same hill is a "deeper" obstacle at higher frequency: lower frequencies diffract better. This is one reason VHF/UHF are preferred for ground-level links in hilly country.

Real terrain has several ridges. Their effects are not independent — each ridge shadows the next — and the popular approximate methods for combining them give different answers. For planning, compute more than one and treat the spread as your uncertainty.

## The math

### Level 1 — formulas and symbols
- $d_1, d_2$ (m): distances from each terminal to the edge; $h$ (m): edge height above the straight line joining the terminals; $\lambda$ (m).
- $v = h\sqrt{\dfrac{2}{\lambda}\left(\dfrac{1}{d_1} + \dfrac{1}{d_2}\right)}$; equivalently $v = \sqrt{2}\,h/R_1$, or with the diffraction angle $\theta$ (radians, change of ray direction at the edge), $v = \theta\sqrt{\dfrac{2d_1d_2}{\lambda(d_1+d_2)}}$.
- Practical form (P.526 eq. 33): $v = 0.0316\,h\sqrt{\dfrac{2(d_1+d_2)}{\lambda d_1d_2}}$ with $d$ in km, $h$ and $\lambda$ in m.
- Loss: $J(v)$ exact via Fresnel integrals $C(v), S(v)$:
$$J(v) = -20\log_{10}\left(\frac{\sqrt{[1 - C(v) - S(v)]^2 + [C(v) - S(v)]^2}}{2}\right)$$
- P.526 approximation (eq. 31): $J(v) \approx 6.9 + 20\log_{10}\left(\sqrt{(v-0.1)^2 + 1} + v - 0.1\right)$, $v > -0.78$ (take 0 dB otherwise).
- Total path loss over one isolated edge: $L = L_\text{FS}(d_1 + d_2) + J(v)$ (ignoring ground reflections on each sub-path).

### Level 2 — derivation (Fresnel–Kirchhoff)
Consider a plane wave (or a source far away) incident on an infinite half-plane screen, and integrate the Huygens secondary sources over the open part of the aperture (Kirchhoff approximation). With paraxial expansion of the path length, the field behind the edge relative to free space is
$$\frac{E}{E_0} = \frac{1+j}{2}\int_v^\infty e^{-j\pi t^2/2}\,dt = \frac{1+j}{2}\left[\left(\tfrac12 - C(v)\right) - j\left(\tfrac12 - S(v)\right)\right],$$
where $v$ is the edge position normalised to the Fresnel scale $\sqrt{\lambda d_1d_2/(2(d_1+d_2))}$. At $v = 0$ the integral is half the full integral (whose magnitude is $\sqrt2$), so $|E/E_0| = \tfrac12$: **−6.02 dB**. For $v \to +\infty$, $\int_v^\infty e^{-j\pi t^2/2}dt \approx \frac{e^{-j\pi v^2/2}}{j\pi v}$, so $|E/E_0| \approx \frac{1}{\pi v\sqrt2}$ ⇒ $J \approx 20\log_{10}(\pi\sqrt2\,v) = 12.95 + 20\log_{10}v$. For $v \to -\infty$ the field oscillates around 1 (ripple from the edge contribution), the ±1.4 dB wiggles of the exact curve. The script evaluates this with `scipy.special.fresnel` and compares with the ITU approximation.

**The ITU approximation's accuracy.** Tabulated: $v$ = 0: 6.02 (exact) vs 6.03 (approx.); 0.5: 10.23 vs 10.29; 1: 13.86 vs 13.93; 2: 19.09 vs 19.04; 3: 22.52 vs 22.42; 5: 26.94 vs 26.81; 10: 32.95 vs 32.86 dB. Maximum error 0.12 dB (at $v$ ≈ 4.6) — far smaller than terrain-modelling uncertainty.

### Level 3 — rounded obstacles, multiple edges and validity
**Rounded obstacle (P.526 §4.2).** A hill with radius of curvature $R$ at the crest adds $T(m,n)$ to $J(v)$ ($m$, $n$ depend on $R$, geometry and $\lambda$), e.g. $T = 7.2m^{1/2} - (2 - 12.5n)m + 3.6m^{3/2} - 0.8m^2$ for $mn \le 4$ [1]. Broad, rounded hills lose several dB more than an ideal knife edge of the same height; buildings and ridges with sharp crests are closer to knife edges. An obstacle is "smooth" if surface irregularities are below $0.04(R\lambda^2)^{1/3}$ (P.526 eq. 5).

**Multiple edges.**
- *Bullington* (single equivalent edge): extend the steepest ray from each terminal over the obstacles; their intersection is an equivalent knife edge. Simple, generally optimistic for multiple obstacles; ITU-R P.526 uses a "delta-Bullington" refinement in its general terrain method.
- *Epstein–Peterson* (1953): compute each edge's loss with the neighbouring edges (or terminals) as endpoints and add. Tends to underestimate when edges are close together.
- *Deygout* (1966): find the edge with the largest $v$ for the whole path (main edge), compute its loss, then apply the same procedure recursively to the sub-paths terminal→main edge and main edge→terminal. Often pessimistic by a few dB when two edges have similar $v$; P.526 includes corrections for this.
Example (script): GS at 5 m, rocket 0.3 m high at 6 km, ridges 18 m at 2 km and 25 m at 4.5 km: at 433 MHz Deygout 23.0, Epstein–Peterson 21.8, Bullington 16.3 dB; at 915 MHz 26.6 / 25.2 / 19.2 dB. The 7 dB spread is typical.

**Validity.** Knife-edge theory assumes a thin, perfectly absorbing edge, scalar paraxial optics ($h$, $R_1$ ≪ $d_1$, $d_2$) and no ground reflections. Near the ground, the reflected rays on each side of the obstacle add their own interference (the "four-ray" knife-edge model), sometimes producing *obstacle gain* in special geometries. Polarisation effects appear only for conducting edges close to the antenna. For long paths over irregular terrain use a full terrain method (P.526 general method, P.1812, ITM) rather than hand-picked edges ([empirical-path-loss-models](empirical-path-loss-models.md)).

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $v = \sqrt2\,h/R_1$ | paraxial single edge | 433 MHz, 25 m edge 1.5 km from a 6 km path end: v ≈ 1.2–1.3 |
| $J(0)$ = 6.02 dB | grazing | |
| $J(v) \approx 13 + 20\log v$ | $v \gtrsim 2$ | v = 5: 27 dB |
| $J \approx 0$ for $v \le -0.8$ | 60 % clearance | |
| ITU approx. error ≤ 0.12 dB | $-0.7 \le v \le 10$ | |
| $\Delta J \approx 10\log(f_2/f_1)$ | deep shadow, same geometry | 433 → 915 MHz: +3.2 dB |
| Multiple edges: Deygout ≥ Epstein–Peterson ≥ Bullington (usually) | | spread 5–10 dB |

## Worked examples
**1 — v from geometry.** 433.125 MHz ($\lambda$ = 0.692 m), edge 4.5 km from one end and 1.5 km from the other, 25 m above the line: $R_1 = \sqrt{0.692\cdot4500\cdot1500/6000} = 27.9$ m; $v = \sqrt2\cdot25/27.9 = 1.267$; $J$ ≈ 15.6 dB (P.526 form via the km formula gives the same $v$ = 1.266).

**2 — Landed rocket behind a ridge.** GS mast 5 m, rocket antenna 0.3 m, 6 km apart; a 25 m ridge 1.5 km in front of the rocket. The edge height above the (sloping) line from 5 m to 0.3 m gives $v$ = 1.19 at 433 MHz: $J$ = 15.1 dB (exact 15.1); at 915 MHz $v$ = 1.73, $J$ = 17.9 dB. Adding to FSPL (100.7/107.2 dB) gives 115.9/125.1 dB — but the terminals are near the ground, so each sub-path also has ground reflection; a fuller estimate uses two-ray on each side or ITM. Compared with the flat-ground landed case (≈ 139 dB at 5 km for a 0.3 m V-pol whip, [two-ray-ground-reflection](two-ray-ground-reflection.md)), the ridge is not necessarily worse than flat ground — both mechanisms interact, and in hilly country a crest can act as a relay-like edge.

**3 — Two ridges.** Adding an 18 m ridge at 2 km: 23.0 dB (Deygout) vs 21.8 (Epstein–Peterson) vs 16.3 (Bullington) at 433 MHz. Budget with the pessimistic value; if the link must work, move the ground station so one ridge is out of the path (a hilltop GS turns both ridges into clearance).

**4 — Buildings on a campus link.** A 915 MHz link across a campus, 800 m, with a 15 m building 200 m from one node (antennas 3 m): the building is 12 m above the ray; $R_1 = \sqrt{0.328\cdot200\cdot600/800} = 7.0$ m; $v$ = 2.42; $J$ ≈ 20.7 dB. Raising the node to the rooftop removes it.

## Practical notes
- **Find the dominant edges from a DEM profile** (SRTM 30 m) plus canopy/building height; knife-edge on the dominant 1–3 edges is usually within the terrain uncertainty.
- **Lower frequency diffracts better** but the difference is modest (~3 dB between 433 and 915 MHz in deep shadow); antenna height and GS siting matter far more.
- **Reflection instead of diffraction.** When a direct path to a repeater or ground station is blocked by buildings, a directional antenna aimed at a large reflecting surface (a building face, a hillside) can find a reflected path that beats the diffraction loss. Hams use this to reach blocked repeaters. Check it by rotating the beam and watching RSSI. A smooth reflecting surface many Fresnel-zone widths across behaves like a mirror ([two-ray](two-ray-ground-reflection.md)).
- **Recovery strategy:** from the predicted landing ellipse, identify ridges between it and the GS; a portable receiver carried to a nearby crest can turn a 20 dB shadow into LOS.

## Common mistakes & misconceptions
- **"If I can't see it, the link is dead."** A few ridges typically cost 10–30 dB, not infinity; LoRa's 140+ dB budgets often survive.
- **"If I can see it, there's no obstacle loss."** Grazing LOS costs 6 dB; partial Fresnel obstruction costs 0–6 dB.
- **Adding knife-edge losses of closely spaced edges independently** (Epstein–Peterson) or trusting one method's answer to better than ±5 dB.
- **Forgetting that $h$ is measured from the line joining the antennas**, not from the ground.
- **Assuming diffraction loss is the same at all frequencies** — it scales with $v \propto \sqrt f$.

## How to simulate / verify
- `tools/verify/prop_knife_edge.py` — exact $J(v)$ (Fresnel integrals), ITU approximation and asymptote, error bound, $v$ from geometry (both forms), single-edge, Deygout, Epstein–Peterson and Bullington on a two-ridge landed-rocket profile at 433/915 MHz.
- ITU-R P.526's full terrain method, ITM, or P.1812 implementations for real profiles; EM solvers (FDTD/parabolic-equation) for research-grade checks.

## Open questions / gaps
- No real launch-site terrain profile has been evaluated (needs DEM + predicted landing ellipse; domain 20).
- Four-ray (knife-edge + ground reflection) model not implemented; it would refine landed-rocket predictions.

## Sources
1. ITU-R Recommendation P.526-14 (01/2018), *Propagation by diffraction*: §2.1 Fresnel ellipsoids, §4.1 single knife edge (eqs. 26–31, J(v) exact and approximation), §4.2 rounded obstacle (eqs. 32–36), §4.5 Bullington, multiple-edge methods. https://www.itu.int/rec/R-REC-P.526/en (standard)
2. J. Deygout, "Multiple knife-edge diffraction of microwaves," *IEEE Trans. Antennas Propag.* AP-14(4), 480–489 (1966). (peer-reviewed)
3. J. Epstein, D. W. Peterson, "An experimental study of wave propagation at 850 Mc," *Proc. IRE* 41(5), 595–611 (1953). (peer-reviewed)
4. K. Bullington, "Radio propagation at frequencies above 30 megacycles," *Proc. IRE* 35(10), 1122–1136 (1947); and "Radio propagation fundamentals," *BSTJ* 36(3), 593–626 (1957). (peer-reviewed)
5. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, §4.7 (knife-edge diffraction, Fresnel–Kirchhoff parameter, multiple edges). (textbook)
6. S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., 2007, ch. 6 (diffraction; comparison of multiple-edge methods). (textbook)
7. `tools/verify/prop_knife_edge.py` (this KB).
