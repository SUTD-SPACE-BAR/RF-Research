---
title: Atmospheric gases, rain, fog, vegetation and building attenuation
domain: 09-propagation-link-budget
slug: atmospheric-rain-attenuation
tags: [gaseous-absorption, ITU-R-P.676, oxygen-60GHz, water-vapour-22GHz, rain-attenuation, ITU-R-P.838, fog, ITU-R-P.840, vegetation, foliage, weissberger, ITU-R-P.833, building-entry-loss, ITU-R-P.2109, mmWave]
prerequisites: [friis-free-space-path-loss.md, ../02-electromagnetics/dielectrics-permittivity-loss-tangent.md]
related: [link-budget-methodology.md, empirical-path-loss-models.md, link-margin-availability.md, ../11-radar/fmcw-radar.md, ../11-radar/radar-range-equation.md]
level: mixed
confidence: high
last_updated: 2026-09-29
---

# Atmospheric gases, rain, fog, vegetation and building attenuation

## Questions this page answers
- Does the atmosphere or rain attenuate my 433/915 MHz telemetry?
- Why are 22 GHz and 60 GHz "bad" frequencies for long links, and why is 60 GHz used for short-range radios?
- How much does heavy tropical rain attenuate a 24 GHz or 77 GHz radar?
- Does fog or cloud matter?
- How much loss do trees add if the rocket lands in a forest?
- How much signal do I lose if my ground station is indoors?
- Do higher frequencies penetrate walls better than lower ones?

## TL;DR
- **Gases (ITU-R P.676-11, sea level, 15 °C, 7.5 g/m³), verified line-by-line implementation** (`tools/verify/prop_atmospheric.py`): 433 MHz **0.0025 dB/km**; 915 MHz 0.005; 1.575 GHz 0.0064; 2.45 GHz 0.0071; 10 GHz 0.014; **22.235 GHz 0.19** (H₂O line); 24 GHz 0.17; 35 GHz 0.10; **60 GHz 14.7 dB/km** (O₂ complex); 77 GHz 0.34; 94 GHz 0.40; 183 GHz 28 dB/km. Tropical air (30 °C, 20 g/m³): 24 GHz 0.43, 77 GHz 0.77 dB/km.
- **Rain (ITU-R P.838-3):** $\gamma_R = kR^\alpha$ dB/km. At 25 mm/h: 2.45 GHz 0.005, 5.8 GHz 0.10, 10 GHz 0.70, **24 GHz 3.7, 60 GHz 10.1, 77 GHz 11.4 dB/km**; at 150 mm/h (a tropical-downpour rate) 77 GHz reaches 41 dB/km. At 433/915 MHz, < 0.003 dB/km even at 150 mm/h (extrapolated; P.838 starts at 1 GHz).
- **Fog/cloud (P.840):** $K_l$ = 0.00013 (433 MHz) … 3.1 (77 GHz) (dB/km)/(g/m³); thick fog (0.5 g/m³) at 77 GHz ≈ 1.6 dB/km; negligible below ~10 GHz.
- **Vegetation (P.833-9):** $A = A_m[1 - e^{-d\gamma/A_m}]$; measured at 466 MHz: γ = 0.12 dB/m, $A_m$ = 18 dB; at 949 MHz: 0.17 dB/m, 26.5 dB. **A rocket 100 m inside woodland loses ~9 dB at 433 MHz, ~12.5 dB at 915 MHz**; Weissberger's model gives roughly double.
- **Buildings (P.2109-2):** median entry loss ≈ **14 dB** (traditional) or **≈ 31–33 dB** (thermally-efficient, metallised glass) at 433–915 MHz, with 10–90 % spreads of ~18–29 dB. **Wall loss rises with frequency** for ordinary materials (a 20 cm concrete wall: ≈ 5 dB at 433 MHz → 15 dB at 2.45 GHz → ≈ 90 dB at 28 GHz, ITU-R P.2040-3) — lower frequencies penetrate better, not worse.
- **Bottom line for Marcus:** for the UHF telemetry the atmosphere is irrelevant (≤ 0.2 dB over 30 km), but **trees and buildings are not**. For 24/60/77 GHz radar, gases and rain dominate range at hundreds of metres to km.

## Intuition (no math)
Air is almost transparent to radio at UHF. Molecules absorb only near their resonances: water vapour has a rotational line at 22.2 GHz (and much stronger ones at 183 GHz and above); oxygen has a magnetic-dipole band of dozens of lines around 60 GHz and one at 119 GHz. Away from these lines, the "wings" of the resonances give a slowly rising background. At 433 MHz the loss is a few thousandths of a dB per km — you would need to cross the entire atmosphere many times to lose a dB.

Rain drops are small compared with a UHF wavelength (70 cm at 433 MHz), so they scatter and absorb almost nothing (Rayleigh regime: loss ∝ $f^2$ and tiny). At 10–100 GHz the drops (1–5 mm) are comparable to the wavelength and become efficient absorbers and scatterers: heavy rain costs several to tens of dB per km. Fog droplets are much smaller than rain drops, so fog only matters at millimetre waves.

Trees are a different matter: wet wood and leaves are lossy dielectrics, and a forest is a random maze of scatterers at every frequency. Buildings add walls, glass (metallised glass is nearly a mirror) and floors.

## The math

### Level 1 — formulas
- **Gaseous specific attenuation (P.676-11 Annex 1):** $\gamma = \gamma_o + \gamma_w = 0.1820\,f\,[N''_\text{Oxygen}(f) + N''_\text{WaterVapour}(f)]$ dB/km, $f$ in GHz; $N''$ = sums over 44 O₂ and 35 H₂O spectral lines (strength $S_i$ × line shape $F_i$) plus a dry continuum [1].
- **Rain (P.838-3):** $\gamma_R = kR^\alpha$ dB/km, $R$ in mm/h; $k, \alpha$ from regression formulas (1–1000 GHz) for H and V polarisation, combined for circular/slant: $k = [k_H + k_V + (k_H - k_V)\cos^2\theta\cos2\tau]/2$ [2].
- **Cloud/fog (P.840):** $\gamma_c = K_l(f, T)\,M$ dB/km, $M$ = liquid water density (g/m³; ~0.05 medium fog with ~300 m visibility, ~0.5 thick fog with ~50 m visibility) [3].
- **Vegetation, terminal inside woodland (P.833-9 eq. 1):** $A_{ev} = A_m[1 - \exp(-d\gamma/A_m)]$ dB ($d$ = depth into woodland, m; γ = short-path specific attenuation, dB/m; $A_m$ = maximum excess loss limited by propagation over/around the canopy) [4].
- **Weissberger (1982):** $L = 1.33f^{0.284}d^{0.588}$ dB (14 < $d$ ≤ 400 m), $0.45f^{0.284}d$ ($d$ < 14 m); $f$ GHz, $d$ m [5]. Early ITU-R/CCIR: $L = 0.2f_\text{MHz}^{0.3}d^{0.6}$.
- **Building entry loss (P.2109-2):** loss not exceeded with probability $P$: $L(P) = 10\log_{10}(10^{0.1A} + 10^{0.1B} + 10^{0.1C})$ with two lognormal components $A = F^{-1}(P)\sigma_1 + \mu_1$, $B = F^{-1}(P)\sigma_2 + \mu_2$, $C$ = −3 dB, $\mu_1 = r + s\log f + t(\log f)^2 + 0.212|\theta|$, $\mu_2 = w + x\log f$, $\sigma_1 = u + v\log f$, $\sigma_2 = y + z\log f$ ($f$ GHz, θ façade elevation angle); coefficients per building class (Table 1) [6].
- **Path attenuation:** $A = \gamma L$ for a uniform medium; for slant paths through the atmosphere integrate over height (P.676 §2.2, equivalent heights); for rain use an effective path length (rain cells are finite; P.530/P.618).

### Level 2 — the physics behind the curves
**Line absorption.** A molecular resonance at $f_i$ produces a pressure-broadened (van Vleck–Weisskopf-type) line shape; P.676 adds Zeeman splitting (O₂), Doppler broadening (H₂O), line-mixing corrections (O₂ near 60 GHz) and a water-vapour pseudo-line at 1780 GHz for the excess continuum. At sea level the ~40 O₂ lines between 50 and 70 GHz merge into one band (14.7 dB/km at 60 GHz); at altitude (lower pressure) they separate — which is why the zenith attenuation through the whole atmosphere at 60 GHz is huge but a path at 20 km altitude sees resolved lines. The implementation here reproduces P.676's reference points (0.19 dB/km at 22.235 GHz, 14.7 at 60 GHz, 28 at 183.31 GHz with 7.5 g/m³).

**Why rain loss rises then saturates.** In the Rayleigh regime (drop radius $a \ll \lambda$) absorption per drop ∝ $a^3/\lambda$, so $\gamma_R \propto f^2$ at low frequency — and small. Around 10–100 GHz ($2\pi a \sim \lambda$) the Mie regime gives a peak in extinction per unit water; above ~100 GHz $\gamma_R$ flattens ($\alpha$ < 1, $k$ ~ 1.2–1.4 per P.838). P.838's $k$ rises from 2.6×10⁻⁵ (1 GHz) to 0.0122 (10 GHz), 0.143 (24 GHz), 0.861 (60 GHz), 1.13 (77 GHz) — verified against its Table 5 to 4 significant figures.

**Polarisation.** Falling drops are oblate (flattened), so horizontal polarisation suffers slightly more rain loss than vertical ($k_H > k_V$ between ~5 and 50 GHz) — and rain causes depolarisation (cross-polar coupling), relevant for polarisation-diversity or dual-pol radar.

**Why walls get worse with frequency.** A wall is a lossy dielectric slab. For a low-loss dielectric the attenuation rate is $\alpha = \tfrac{\sigma}{2}\sqrt{\mu_0/(\varepsilon_0\varepsilon')}$ Np/m, i.e. $A \approx 1636\,\sigma/\sqrt{\varepsilon'}$ dB/m (ITU-R P.2040-3 eq. 27 [9]), and measured building materials have a conductivity that *grows* with frequency, $\sigma = c f^d$ with $d$ ≈ 0.8 (concrete), 0.94 (plasterboard), 1.07 (wood), 1.34 (glass) (P.2040-3 Table 3). With $\varepsilon'$ roughly constant, the loss in dB through a given thickness therefore rises as $f^d$. `tools/verify/fix_penetration_vs_frequency.py` (exact slab transmission with internal reflections) gives, for 20 cm of concrete, 5.3 / 7.4 / 14.8 / 27.5 / 41.4 / 90.9 dB at 0.433 / 0.915 / 2.45 / 5.8 / 10 / 28 GHz (below 1 GHz the Table 3 fit is an extrapolation). P.2109-2's empirical building-entry loss shows the same trend for traditional buildings (13.9 → 15.2 → 20.2 → 24.0 dB at 0.433 / 2.45 / 28 / 100 GHz, with a very shallow minimum near 0.3–0.5 GHz); thermally-efficient buildings are the exception at low UHF (40.2 dB at 100 MHz, 32.7 at 433 MHz, minimum ≈ 30.6 dB near 2.45 GHz, then 41.7 at 28 GHz) because metallised glass and foil-backed insulation are nearly opaque and energy leaks through apertures and seams, which pass shorter wavelengths more easily (an aperture below ~λ/2 is cut off).

**Vegetation saturation.** For a terminal deep in a wood, energy reaches it mainly by propagating over the canopy and diffracting/scattering down, so excess loss saturates at $A_m$ rather than growing linearly with depth — P.833's exponential form. Weissberger's model, a power-law fit to older data, keeps growing and is more pessimistic at depth.

### Level 3 — limits and details
- **P.838 is valid 1–1000 GHz**; below 1 GHz the script extrapolates with $f^2$ scaling (physically the Rayleigh regime) and flags it. Either way it is ≪ 0.01 dB/km.
- **P.676-11 vs newer revisions:** later revisions (-12, -13) revised spectroscopic data and the approximate Annex 2; differences are small away from line centres. The implementation uses -11 as read.
- **Rain statistics:** design uses the rain rate exceeded for 0.01 % of an average year ($R_{0.01}$, ITU-R P.837 maps) and path-reduction factors (P.530 for terrestrial, P.618 for Earth–space). Tropical climates (Singapore) have among the highest $R_{0.01}$ values in the world (above 100 mm/h; P.837 value not extracted here).
- **Wet radomes/antennas:** a water film on a radome or on a patch antenna can cost several dB at X/K/mm-wave — often more than the rain path itself for short radar paths.
- **Snow, sand/dust, and hail** have their own models; irrelevant at UHF.
- **Building entry loss** is statistical (P.2109 validated for probabilities 0.01–0.99 from measurements 80 MHz–73 GHz) and does not include surrounding clutter (P.2108).

## Design equations & rules of thumb

| Quantity | 433 MHz | 915 MHz | 2.45 GHz | 24 GHz | 60 GHz | 77 GHz |
|---|---|---|---|---|---|---|
| Gases, sea level, 7.5 g/m³ (dB/km) | 0.0025 | 0.0051 | 0.0071 | 0.17 | 14.7 | 0.34 |
| Gases, tropical 30 °C, 20 g/m³ | 0.0023 | – | – | 0.43 | 13.0 | 0.77 |
| Rain 25 mm/h (dB/km, H) | ~0.0001 | ~0.0005 | 0.005 | 3.7 | 10.1 | 11.4 |
| Rain 100 mm/h | ~0.0004 | ~0.002 | 0.022 | 14.9 | 29.2 | 30.8 |
| Fog 0.5 g/m³ (dB/km) | 6×10⁻⁵ | 3×10⁻⁴ | 0.002 | 0.19 | 1.05 | 1.57 |
| Woodland, 100 m in (P.833 Table 1) | 8.8 dB (466 MHz) | 12.5 dB (949 MHz) | – | – | – | – |
| Building entry, median (P.2109, traditional / thermally-eff.) | 13.9 / 32.7 dB | 14.3 / 31.1 dB | 15.2 / 30.6 dB | – | – | – |

## Worked examples
**1 — 30 km telemetry path.** Sea-level specific attenuation at 433 MHz × 30 km = 0.076 dB (a slant path to a rocket at altitude sees thinner air, so less). Rain at 25 mm/h over 5 km: 0.001 dB. At 915 MHz: 0.15 dB and 0.002 dB. Budget line: 0.1–0.15 dB — the link budget uses 0.1 dB ([link-budget-methodology](link-budget-methodology.md)).

**2 — 77 GHz automotive-style radar in a tropical downpour.** Two-way path to a target at 150 m: gases (tropical) 0.77 dB/km × 0.3 km = 0.23 dB; rain at 100 mm/h: 30.8 × 0.3 = 9.2 dB two-way. At 150 mm/h, 41.3 dB/km × 0.3 = 12.4 dB. A radar designed with 10 dB SNR margin at 150 m loses the target in heavy rain; range in rain shrinks roughly where the (two-way) rain loss equals the margin. See [11-radar/radar-range-equation](../11-radar/radar-range-equation.md).

**3 — 60 GHz for short-range links.** 14.7 dB/km of oxygen absorption: negligible across a room (0.15 dB over 10 m) but 15 dB over 1 km — natural isolation that allows dense frequency reuse and low-probability-of-intercept links.

**4 — Rocket landed in woodland.** At 433 MHz, 50 m inside a wood: 5.1 dB (P.833 Table 1 values at 466 MHz); 100 m: 8.8 dB; 300 m: 15.6 dB (saturating toward 18 dB). Weissberger gives 10.7 / 16.1 / 30.6 dB and the early ITU formula 13.2 / 20.0 / 38.7 dB for the same depths — the spread between models (up to ~2×) is typical of vegetation predictions. Combine with the plane-earth loss of the landed case (≈ 154 dB at 5 km) and there is little margin left at 2.4 kb/s; SF12 buys ~9 dB.

**5 — Ground station indoors.** A 433 MHz receiver behind a window in a traditional building loses a median 14 dB (10 % of locations < 5.7 dB, 90 % < 23.8 dB); in a modern thermally-efficient building a median 33 dB — go outside or put the antenna on the roof.

## Practical notes
- **Keep antennas dry** at microwave frequencies (radome shape, hydrophobic coatings); at UHF, rain on a Yagi mainly detunes it slightly.
- **Seasonal foliage** changes attenuation (P.833 notes ~20 % higher specific attenuation in leaf at ~1 GHz and wind-induced fading).
- **For GNSS**, tree canopy attenuates L1 by several dB and causes multipath — relevant to recovery by GNSS position (last fix may be degraded under trees).

## Common mistakes & misconceptions
- **Adding "rain fade" to a UHF LoRa link budget.** It is below 0.01 dB; rain matters to LoRa only through wet antennas and increased vegetation loss.
- **Assuming higher frequency always suffers more atmospheric loss.** 77 GHz (0.34 dB/km) is far better than 60 GHz (14.7 dB/km) and even better than 22 GHz in humid air in some conditions; the spectrum has windows (35, 94, 140 GHz) between absorption lines.
- **Using Weissberger or the early ITU formula outside their depth range** (≤ 400 m) or treating their output as accurate to better than ±5–10 dB.
- **Forgetting building entry loss when testing from inside a lab** — a "range test" through a window can be 15–30 dB pessimistic.
- **"Higher frequencies penetrate walls better."** For ordinary building materials the opposite is true across the RF range: conductivity rises as $f^{0.8\text{–}1.3}$ (P.2040-3 Table 3), so 20 cm of concrete costs ≈ 5 dB at 433 MHz, 7 dB at 915 MHz, 15 dB at 2.45 GHz, 28 dB at 5.8 GHz and ≈ 90 dB at 28 GHz, and P.2109-2 traditional-building entry loss rises from 13.9 dB (433 MHz) to 24 dB (100 GHz) [6][9]. What feeds the myth: (i) thermally-efficient (metallised-glass) buildings, where P.2109 entry loss is *lower* at 2.45 GHz (30.6 dB) than at 433 MHz (32.7 dB) because energy enters through apertures; (ii) thickness resonances of thin slabs (single glazing, one brick) that make individual measurements non-monotonic; (iii) confusion with optical transparency (a different regime) and with the free-space "higher f loses more" myth, which is an aperture effect ([Friis](friis-free-space-path-loss.md)). For telemetry into or out of a building, the lowest band available wins — 433 MHz beats 2.4 GHz by ~10 dB through a concrete wall. (Myth flagged by W4-D1 from electronics.stackexchange.com/q/33537.)

## How to simulate / verify
- `tools/verify/fix_penetration_vs_frequency.py` — P.2040-3 Table 3 wall-slab transmission (concrete, brick, plasterboard, wood, glass) and P.2109-2 entry loss vs frequency; asserts the rising trend and the thermally-efficient minimum (ALL PASS).
- `tools/verify/prop_atmospheric.py` — P.676-11 line-by-line (tables transcribed from the Recommendation), P.838-3 regression (reproduces Table 5), P.840 double-Debye fog, P.833/Weissberger/early-ITU vegetation, P.2109-2 building entry loss, 30 km path totals.
- The `itur` (ITU-Rpy) Python package implements current P.676/P.838/P.840/P.618 versions if installed; compare against this script for version differences.

## Open questions / gaps
- P.837 rain-rate statistics for Singapore and launch sites not extracted (needed for mm-wave radar/link design, not for UHF telemetry).
- Plume, ionised-exhaust and rocket-fairing losses are covered in [link-budget-methodology](link-budget-methodology.md), not here.
- Vegetation data at exactly 433/915 MHz for tropical forest were not found; P.833 values are from Russian mixed forest and Brazilian/French sites.

## Sources
1. ITU-R Recommendation P.676-11 (09/2016), *Attenuation by atmospheric gases*, Annex 1 eqs. (1)–(9), Tables 1–2. https://www.itu.int/rec/R-REC-P.676/en (standard)
2. ITU-R Recommendation P.838-3 (03/2005), *Specific attenuation model for rain for use in prediction methods*, eqs. (1)–(5), Tables 1–5. https://www.itu.int/rec/R-REC-P.838/en (standard)
3. ITU-R Recommendation P.840-8 (08/2019), *Attenuation due to clouds and fog*, §2 eqs. (2)–(11); liquid water density examples. https://www.itu.int/rec/R-REC-P.840/en (standard)
4. ITU-R Recommendation P.833-9 (09/2016), *Attenuation in vegetation*, §2.1 eq. (1)–(2), Table 1 (St Petersburg measurements), $A_m = A_1f^\alpha$ fits. https://www.itu.int/rec/R-REC-P.833/en (standard)
5. M. A. Weissberger, "An initial critical summary of models for predicting the attenuation of radio waves by trees," ECAC-TR-81-101, Electromagnetic Compatibility Analysis Center, 1982. (technical report) *cited via secondary sources*
6. ITU-R Recommendation P.2109-2 (08/2023), *Prediction of building entry loss*, eqs. (1)–(10), Table 1. https://www.itu.int/rec/R-REC-P.2109/en (standard)
7. J. S. Seybold, *Introduction to RF Propagation*, Wiley 2005, ch. 7–8 (atmospheric and rain effects, foliage models). (textbook)
8. `tools/verify/prop_atmospheric.py` (this KB).
9. ITU-R Recommendation P.2040-3 (08/2023), *Effects of building materials and structures on radiowave propagation above about 100 MHz* — eq. (27) low-loss attenuation rate, eqs. (28)–(29) frequency models, Table 3 material parameters (concrete a = 5.24, c = 0.0462, d = 0.7822, valid 1–100 GHz; etc.). https://www.itu.int/rec/R-REC-P.2040/en (standard; PDF read with pdftotext 2026-09-29)
