---
title: Lens, reflectarray and transmitarray antennas — dielectric lenses for mm-wave radar, Luneburg lenses, zoning, phase quantisation, why lenses are rare below mm-wave
domain: 08-antennas
slug: lens-and-reflectarray-antennas
tags: [lens, dielectric-lens, hyperbolic-lens, luneburg, fresnel-zone-plate, zoning, reflectarray, transmitarray, phase-quantization, 3d-printing, mmwave, 24-ghz, 77-ghz, radar]
prerequisites: [horn-reflector-aperture-antennas.md, antenna-fundamentals.md, ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md]
related: [patch-antennas.md, ../11-radar/diy-radar-hardware.md, ../11-radar/radar-cross-section.md, ../12-phased-arrays/phase-shifters-ttd-components.md, ../12-phased-arrays/planar-arrays-element-pattern-coupling.md, slot-antennas.md]
level: intermediate
confidence: medium
last_updated: 2026-10-02
---

# Lens, reflectarray and transmitarray antennas

## Questions this page answers
- Why don't we use lenses for RF the way we do for light?
- Can I put a 3D-printed lens in front of my 24 GHz or 77 GHz radar module, and how much gain does it add?
- How is a dielectric lens shaped, and how thick is it?
- What is a Luneburg lens and why is it used for radar reflectors?
- What are zoned (Fresnel) lenses and zone plates?
- What is a reflectarray / transmitarray and how does it differ from a dish or a phased array?
- How much gain do I lose with 1-bit or 2-bit element phases?
- What limits the bandwidth of a reflectarray?

## TL;DR
- A lens is an aperture antenna: **G ≈ e_ap(πD/λ)²** with e_ap ≈ 0.5–0.65, so it is only worthwhile when D ≫ λ (≳ 5–10 λ). That is why lenses appear at mm-wave (λ = 3.9 mm at 77 GHz, 12.5 mm at 24 GHz) and almost never below a few GHz: a 5λ PTFE lens at 433 MHz would be 3.5 m across and weigh ≈ 8 t (`tools/verify/ant2_lens.py`), whereas a dish of the same aperture is a thin metal shell.
- **Hyperbolic plano-convex lens** (point source at the focus, flat exit face): $r(\theta)=\frac{(n-1)F}{n\cos\theta-1}$, n = √εr. Verified: equal electrical path across the aperture to 10⁻¹³ mm.
- **Worked numbers** (F/D = 1, e_ap = 0.55): 50 mm lens at 77 GHz → **29.5 dBi, HPBW ≈ 5.5°**, convex height 8–11 mm, dielectric loss 0.02 dB (PTFE) / 0.7 dB (printed PLA, tan δ 0.015); 100 mm PLA lens at 24 GHz → **25.4 dBi, 8.7°**, loss ≈ 0.4 dB + ≈ 0.5 dB surface reflections.
- **Zoning**: remove material in steps of λ/(n − 1) (1.6–2.2 λ for εr 2.1–2.6) to make thin Fresnel lenses — lighter, but narrowband and with zone-edge shadowing losses.
- **Luneburg lens**: graded index $n(r)=\sqrt{2-(r/R)^2}$ focuses a plane wave from *any* direction onto the opposite surface point — wide-angle multibeam antennas and passive radar reflectors. Our ray trace: exit rays parallel to 4 × 10⁻⁷°.
- **Reflectarray / transmitarray**: a flat array of passive elements (patches of varying size, slots, phase-delay lines) illuminated by a feed; each element re-radiates with the phase that a dish or lens surface would provide. Phase quantisation loss: **1-bit −3.9 dB, 2-bit −0.9 dB, 3-bit −0.2 dB** (verified). The spatial phase-delay bandwidth shrinks with aperture: a 30 cm (10 λ) X-band reflectarray loses 0.07 dB at ±5 %, a 1 m one 0.8 dB, a 3 m one 9 dB — before element bandwidth (usually the real limit) is counted.

## Intuition (no math)
A lens works by slowing the wave down more in the middle than at the edges: a spherical wave from the feed spreads out, and the lens delays the centre rays just enough that all rays arrive at the far face in step — a flat wavefront, i.e. a beam. The thickness needed is a few wavelengths of extra delay, so the lens's *size* is set by wavelength: the bigger the aperture in wavelengths, the higher the gain, and the thicker and heavier the lens.

At optical wavelengths a "huge" lens of 10⁴ wavelengths is a 5 mm glass bead. At 433 MHz a lens of only 5 wavelengths is 3.5 m across. A reflector does the same job with a thin curved metal surface, and an array does it with phase shifters — so below a few GHz lenses lose to dishes and arrays on weight and cost. At 24–300 GHz the trade flips: a palm-sized plastic lens gives 25–35 dBi and doubles as a radome.

A reflectarray is a "flat dish": instead of curving the surface to create the right path lengths, each little patch on a flat board reflects with a built-in phase shift that mimics the curvature. A transmitarray does the same in transmission (a "flat lens").

## The math

### Level 1 — formulas
| Quantity | Formula | Symbols |
|---|---|---|
| Gain | $G=e_{ap}(\pi D/\lambda)^2$ | D aperture diameter; e_ap 0.5–0.65 |
| HPBW | ≈ 70λ/D degrees | moderate taper |
| Hyperbolic lens surface | $r(\theta)=(n-1)F/(n\cos\theta-1)$ | n = √εr, F focal distance to vertex, θ from axis |
| Zone step | $\Delta t=\lambda/(n-1)$ | |
| Dielectric loss | $L\,[\text{dB}]\approx 8.686\,\pi n\tan\delta\,t_{avg}/\lambda_0$ | t_avg average thickness |
| Surface reflection (each face) | $\lvert\Gamma\rvert^2=((n-1)/(n+1))^2$ | normal incidence; matching layer of √n and λ/(4√n) removes it |
| Luneburg index | $n(r)=\sqrt{2-(r/R)^2}$ | R lens radius |
| Reflectarray element phase | $\phi_i=k_0(R_i-\mathbf r_i\cdot\hat{\mathbf u}_0)+\phi_0\ (\text{mod }2\pi)$ | R_i feed–element distance, û₀ beam direction |
| Phase-quantisation loss | $[\mathrm{sinc}(2^{-b})]^2$ | b bits |

### Level 2 — derivations
**Hyperbolic lens (Fermat).** Put the source at the origin and the lens vertex at distance F. A ray at angle θ meets the convex surface at distance r(θ); inside a plano-convex lens with a flat back, all rays then travel parallel to the axis. Equal phase on a plane z = const requires
$$r(\theta)=F+n\,[r(\theta)\cos\theta-F]\ \Rightarrow\ r(\theta)=\frac{(n-1)F}{n\cos\theta-1},$$
a hyperbola with eccentricity n. Our script traces 200 rays and finds the electrical path to the exit plane constant to 8.5 × 10⁻¹⁴ mm. The surface only exists for $\cos\theta>1/n$ (asymptote), which limits the usable feed angle (≈ 51° for n = 1.61) and favours F/D ≳ 0.8–1.
**Luneburg lens.** In a spherically symmetric index n(r), rays obey Bouguer's invariant $n\,r\sin\psi=$ const. Requiring that every ray entering from a point on the surface (where n = 1) exits parallel to the diameter through that point yields $n=\sqrt{2-(r/R)^2}$ (Luneburg 1944). We integrate the ray equation $\frac{d}{ds}(n\,\frac{d\mathbf r}{ds})=\nabla n$ numerically for launch angles 5–85°: every ray exits parallel to the axis (largest error 3.9 × 10⁻⁷°). Practical Luneburg lenses approximate the profile with 5–10 concentric shells of foam or printed lattice (εr from ≈ 2 at the centre to ≈ 1.1 at the skin). Backed by a metal cap, it becomes a wide-angle retro-reflector ([RCS](../11-radar/radar-cross-section.md)).
**Phase quantisation.** If each element's phase error is uniformly distributed in ±π/2^b (rounding to b bits, errors uncorrelated), the coherent sum is reduced by the mean of $e^{j\epsilon}$, i.e. $\mathrm{sinc}(2^{-b})$ in amplitude → loss $20\log\mathrm{sinc}(2^{-b})$: −3.92, −0.91, −0.22, −0.06 dB for 1–4 bits (Monte-Carlo agrees, `ant2_lens.py` §4). The same law governs digital phase shifters in [phased arrays](../12-phased-arrays/phase-shifters-ttd-components.md).
**Spatial phase-delay bandwidth.** A reflectarray element supplies a *phase* (wrapped modulo 2π), whereas a dish supplies a true *path length*. At f₀(1 + Δ) the error at an element is $2\pi(R_i/\lambda_0)\Delta$ minus the wrapped part, i.e. it grows with the feed-to-element path difference across the aperture (1.43 λ for 10 λ at F/D 0.8, 4.8 λ for 33 λ, 14 λ for 100 λ). Aperture-integration results: −0.07 / −0.83 / −9.2 dB at Δ = 5 % for D = 10/33/100 λ. Large reflectarrays therefore use true-time-delay elements or multiple feeds; small ones are limited by element bandwidth instead (a patch element's phase-vs-size curve is steep near resonance, typically giving 3–10 % bandwidth).

## Design equations & rules of thumb
| Item | Value | Notes |
|---|---|---|
| Minimum useful lens size | D ≳ 5–10 λ | below that use a horn or patch array |
| Lens materials | PTFE εr 2.1 (tan δ ~3 × 10⁻⁴), HDPE ≈ 2.3, Rexolite ≈ 2.5, printed ABS 2.57 (0.0047 @ 15 GHz), printed PLA 2.5–2.8 (0.01–0.02) | ([dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md)) |
| Infill printing | effective εr tunable with infill fraction | graded-index lenses printable |
| Surface reflection | 0.3 dB (PTFE) – 0.5 dB (PLA) for two faces | add λ/4 matching grooves |
| 77 GHz, 50 mm lens | ≈ 29.5 dBi, 5.5° | e_ap 0.55 |
| 24 GHz, 100 mm lens | ≈ 25.4 dBi, 8.7° | |
| Zone plate (amplitude) | ≈ 10 % (−10 dB) of a full lens | phase-reversal ≈ 40 % (−4 dB) |
| 2-bit reflectarray | −0.9 dB | 1-bit −3.9 dB |
| Reflectarray bandwidth | element-limited, 3–10 %; spatial delay matters beyond ~30 λ | |

## Worked examples

**Example 1 — Lens for a 24 GHz radar module** (D2 #72, D1 #147, D1 #433 "adding a horn or lens"). A 24 GHz patch-array module has ≈ 10–13 dBi and a ±30° beam. A 100 mm 3D-printed PLA lens (n = 1.61, F = 100 mm, i.e. F/D = 1) with the module at the focus: surface $r(\theta)=61.2/(1.612\cos\theta-1)$ mm; convex height ≈ 16.7 mm (plus a flat base, say 3 mm). Gain ≈ 0.55 × (π × 100/12.49)² → **25.4 dBi**, HPBW ≈ 8.7°; losses ≈ 0.4 dB (PLA) + 0.5 dB reflections; spillover depends on the module's beam — the lens edge is seen from the focus at ±23° (script), so part of a ±30° module beam spills past the rim — a slightly longer F or a bigger lens catches more. Net improvement ≈ +12 dB on each of transmit and receive → **+24 dB two-way** in the radar equation, ≈ 4× range for the same target ([radar range equation](../11-radar/radar-range-equation.md)). Check the EIRP limit of your band before transmitting through it ([19 regulations](../19-regulations-safety/spectrum-allocation-ism-bands.md)).

**Example 2 — Why not at 433 MHz?** For 21 dBi a lens needs D ≈ 5 λ = 3.5 m; the PTFE convex cap alone is ≈ 3.6 m³ ≈ 7.9 t. A 3.5 m mesh dish gives the same gain at a few tens of kg, and a 15-element Yagi gives ≈ 15 dBi at < 2 kg. Lenses are therefore a mm-wave tool.

**Example 3 — 2-bit reflectarray at 10 GHz.** 30 cm (10 λ) aperture, F/D 0.8, patches of 4 sizes giving 0/90/180/270°: quantisation −0.9 dB; spatial-delay loss at ±5 % only −0.07 dB; with e_ap ≈ 0.5 the gain ≈ 10 log(0.5 × (π × 10)²) − 0.9 = 26.9 − 0.9 ≈ **26.0 dBi**. Element bandwidth (patch resonance) will set the usable band (a few %).

## Practical notes
- **Feed placement**: the phase centre of the feed must sit at the lens focus; for a patch module, the phase centre is ≈ at the patch plane. Tune by moving the lens ±λ/4 and maximising received signal on a fixed target.
- **3D printing**: print solid (100 % infill) or deliberately graded infill; check εr of your filament at the frequency (it varies by brand and moisture); avoid fibre-filled filaments (carbon is conductive and lossy).
- **Radome function**: a lens also protects the module; at 77 GHz water/ice on the lens attenuates strongly (rain film losses of several dB).
- **Polarization**: dielectric lenses preserve polarization; reflectarrays reverse CP sense like a dish (unless designed otherwise).
- **Mounting**: keep metal out of the feed-to-lens cone; metal near the edge causes sidelobes.

## Common mistakes & misconceptions
- **"Lenses don't work at RF."** They work exactly like optical lenses when D ≫ λ; they are just impractically large at low frequencies.
- **"A lens adds gain without changing the beam."** Gain comes from narrowing the beam: +12 dB ≈ 4× narrower in each plane; a radar that needed a wide field of view loses it.
- **"Any plastic is transparent."** Filled, wet or carbon-loaded plastics absorb; PLA at 77 GHz costs ≈ 0.7 dB for an 8 mm lens — fine — but black (carbon) filament can be much worse.
- **"A reflectarray is a phased array."** It has no active phase shifters unless they are added (reconfigurable reflectarrays/RIS); its phases are fixed by element geometry.
- **"1-bit phase is good enough."** It costs 3.9 dB and raises quantisation lobes; 2 bits recover 3 dB.
- **"Zoned lenses are as good as solid ones."** They are lighter but narrowband and lose a little at each zone step.

## How to simulate / verify
- `python3 tools/verify/ant2_lens.py` — hyperbolic-lens Fermat check, lens gain/thickness/loss/mass table, Luneburg ray trace, phase-quantisation Monte-Carlo, reflectarray spatial-delay bandwidth vs aperture size. Output in `tools/verify/ant2_lens_output.txt`.
- Full-wave: openEMS can model a small (≤ 10 λ) lens with a patch feed, but cell counts grow as (D/λ)³; ray-optics + aperture integration (as here) is the normal first step.
- Measure: compare received power from a corner reflector at fixed range with and without the lens.

## Open questions / gaps
- No full-wave (openEMS) check of a printed lens with a real radar-module feed; spillover/aperture efficiency (0.55) is an assumption.
- PLA/ABS mm-wave properties vary by brand and moisture; measure your filament (e.g., with a free-space transmission test).
- Reconfigurable intelligent surfaces (RIS) and electronically switched reflectarrays not covered.

## Sources
1. J. D. Kraus and R. J. Marhefka, *Antennas for All Applications*, 3rd ed., 2002 — lens antennas (E-plane metal-plate and dielectric lenses, zoning). (textbook; cited)
2. W. L. Stutzman and G. A. Thiele, *Antenna Theory and Design*, 3rd ed., 2012 — aperture antennas, lens design. (textbook; cited)
3. J. L. Volakis (ed.), *Antenna Engineering Handbook*, 5th ed., 2019 — lens antennas and reflectarray chapters. (handbook; cited)
4. R. K. Luneburg, *Mathematical Theory of Optics*, Brown University lecture notes, 1944 (Univ. of California Press, 1964) — graded-index lens. (book; cited)
5. D. G. Berry, R. G. Malech, W. A. Kennedy, "The reflectarray antenna," *IEEE Trans. Antennas Propag.* 11(6), 645–651, 1963; J. Huang and J. A. Encinar, *Reflectarray Antennas*, Wiley-IEEE, 2008 — element phase, bandwidth (spatial phase delay vs element). (peer-reviewed/book; cited)
6. D. M. Pozar, S. D. Targonski, H. D. Syrigos, "Design of millimeter wave microstrip reflectarrays," *IEEE Trans. Antennas Propag.* 45(2), 287–296, 1997 — variable-size patch elements. (peer-reviewed; cited)
7. This KB: [dielectrics](../02-electromagnetics/dielectrics-permittivity-loss-tangent.md) (PLA/ABS/PTFE values), [aperture antennas](horn-reflector-aperture-antennas.md) (e_ap, taper/spillover), [phase shifters](../12-phased-arrays/phase-shifters-ttd-components.md) (quantisation). (KB)
8. This repository: `tools/verify/ant2_lens.py` (+ `_output.txt`). (verification)
