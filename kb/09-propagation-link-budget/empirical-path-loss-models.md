---
title: Empirical and semi-empirical path-loss models (log-distance, Hata, COST-231, Egli, ITU-R P.528/P.1546/P.1812/P.1411/P.452, Longley–Rice)
domain: 09-propagation-link-budget
slug: empirical-path-loss-models
tags: [path-loss-models, log-distance, shadowing, okumura-hata, COST-231, egli, ITU-R-P.1546, ITU-R-P.1812, ITU-R-P.1411, ITU-R-P.452, ITU-R-P.528, longley-rice, ITM, air-to-ground]
prerequisites: [friis-free-space-path-loss.md, two-ray-ground-reflection.md, fresnel-zones-los-radio-horizon.md]
related: [diffraction-knife-edge.md, multipath-fading-doppler.md, link-margin-availability.md, atmospheric-rain-attenuation.md, link-budget-methodology.md, ../16-simulation-tools/tool-landscape-overview.md, ../15-lora-ism-radios/lora-sensitivity-and-link-budget.md]
level: mixed
confidence: medium
last_updated: 2026-10-14
---

# Empirical and semi-empirical path-loss models

## Questions this page answers
- When should I use free space, plane earth, Hata, Egli, Longley–Rice or an ITU-R method?
- What model applies to a rocket-to-ground link (air-to-ground)?
- What model applies to ground-level LoRa between two people or nodes?
- What is the log-distance model with shadowing, and what path-loss exponents are typical?
- Why do different "calculators" give answers 20 dB apart for the same link?
- What are the validity limits of Okumura–Hata, and what happens when I use it for 2 m antennas?

## TL;DR
- **Choose the model by geometry first:**
  - Elevated rocket, clear sky path → **free space** (+ ground lobing at low elevation). For rigorous statistics, **ITU-R P.528** (air-to-ground, 125 MHz–15.5 GHz, terminals 1.5 m–20 km above sea level, time percentages 1–99 %) [1].
  - Rocket on the ground / ground-level LoRa over open terrain → **two-ray / plane earth** + terrain diffraction; for real terrain **Longley–Rice (ITM, 20 MHz–20 GHz, > 1 km)** [2] or **ITU-R P.1812** (30 MHz–6 GHz, 0.25–3000 km, path-specific) [3]. For a *landed* antenna (< 1 m up) ITM is outside its recommended range and differed from two-ray by **10–50 dB** (less loss) on a real profile in the KB's own run (`rfcalc itm`, [tool landscape Example 4](../16-simulation-tools/tool-landscape-overview.md)): use two-ray to plan, ITM to find terrain shadows.
  - Broadcast/mobile coverage estimates → **ITU-R P.1546** (30–4000 MHz, 1–1000 km, 1–50 % time) [4] or **Okumura–Hata** (150–1500 MHz, base 30–200 m, mobile 1–10 m, 1–20 km) [5].
  - Urban/short range (< 1 km) → **ITU-R P.1411** [6]; interference/ducting over long paths → **ITU-R P.452** [7].
- **Log-distance:** $L(d) = L(d_0) + 10n\log_{10}(d/d_0) + X_\sigma$; $n$ = 2 (free space), ~4 (plane earth), 2.7–5 in built-up areas; shadowing $X_\sigma$ lognormal with σ ≈ 4–12 dB.
- At 433 MHz, base 30 m, mobile 1.5 m, 5 km: FSPL 99.2 dB, plane earth 114.9, Hata-open 116.9, Hata-suburban 134.5, Hata-urban 142.7 dB — a **44 dB spread** set by environment, not by frequency (`tools/verify/prop_empirical.py`).
- **Fit exponents only to data that include the failures.** Received-only (mapper) data are censored: in a simulation with true n = 3.5, least squares on received packets returned **n = 1.7** and a median range 2.4× too long; a censored (Tobit) fit with the failed attempts recovered n = 3.6 ([tool landscape Example 5](../16-simulation-tools/tool-landscape-overview.md)).
- **Hata with 2 m antennas is invalid** (base height outside 30–200 m) — yet many LoRa "range calculators" do exactly that.
- Secondary sources disagree on constants: Egli's dB form (83.9 vs 85.9 vs the 88.0 implied by its own ratio form), Hata's validity (1000 vs 1500 MHz) and open-area coefficient (18.33 vs 19.33) — see Level 3.

## Intuition (no math)
Physical models (free space, two-ray, knife-edge diffraction) describe one mechanism exactly. Real paths combine many: reflection from uneven ground, diffraction over hills, scattering and absorption by trees and buildings. Empirical models fit measured data from campaigns in particular places, and so bundle all these mechanisms into a formula — at the cost of only being valid for conditions like the original measurements.

Okumura drove around Tokyo in the 1960s measuring TV and mobile signals; Hata fitted formulas to Okumura's curves in 1980. Egli fitted US TV data from the 1950s. The ITU-R methods are curve families refined over decades from global measurements, with explicit statistics for time and location variability. Longley and Rice built a semi-physical model (diffraction + troposcatter + terrain statistics) that can use an actual terrain profile.

None of the mobile-radio models were built for a transmitter at 3 km altitude. A rocket in flight is a clean, elevated, free-space-like path; only its low-elevation and landed phases need terrain models.

## The math

### Level 1 — the models
**Free space:** $L = 32.45 + 20\log f_\text{MHz} + 20\log d_\text{km}$ ([friis-free-space-path-loss](friis-free-space-path-loss.md)).

**Plane earth** (isotropic antennas, $d \gg 4h_1h_2/\lambda$): $L = 40\log_{10}d_\text{m} - 20\log_{10}(h_1h_2)$ ([two-ray-ground-reflection](two-ray-ground-reflection.md)).

**Log-distance with lognormal shadowing:**
$$L(d) = L(d_0) + 10\,n\log_{10}\frac{d}{d_0} + X_\sigma,\qquad X_\sigma\sim\mathcal{N}(0,\sigma^2)\ \text{dB}.$$

**Okumura–Hata** (Hata 1980 [5]; $f$ MHz, heights m, $d$ km):
$$L_\text{urban} = 69.55 + 26.16\log f - 13.82\log h_b - a(h_m) + (44.9 - 6.55\log h_b)\log d$$
- small/medium city: $a(h_m) = (1.1\log f - 0.7)h_m - (1.56\log f - 0.8)$
- large city: $a(h_m) = 8.29(\log 1.54h_m)^2 - 1.1$ ($f \le 200$ MHz); $3.2(\log 11.75h_m)^2 - 4.97$ ($f \ge 400$ MHz)
- suburban: $L_\text{urban} - 2[\log(f/28)]^2 - 5.4$
- open: $L_\text{urban} - 4.78(\log f)^2 + 18.33\log f - 40.94$
- Validity: $f$ 150–1500 MHz, $h_b$ 30–200 m, $h_m$ 1–10 m, $d$ 1–20 km.

**COST-231–Hata** (1500–2000 MHz): $L = 46.3 + 33.9\log f - 13.82\log h_b - a(h_m) + (44.9 - 6.55\log h_b)\log d + C_m$, $C_m$ = 0 dB (medium city/suburban), 3 dB (metropolitan) [8].

**Egli** (1957 [9]), ratio form: $\dfrac{P_r}{P_t} = G_bG_m\left(\dfrac{h_bh_m}{d^2}\right)^2\left(\dfrac{40}{f_\text{MHz}}\right)^2$ — plane earth with an extra $f^{-2}$ "terrain" factor, i.e. $L = 88.0 + 20\log f_\text{MHz} + 40\log d_\text{km} - 20\log(h_bh_m)$ for isotropic gains (the frequently quoted variant uses $76.3 - 10\log h_m$ for $h_m <$ 10 m).

### Level 2 — how the physical and empirical pieces relate
- Hata's distance slope $(44.9 - 6.55\log h_b)$ gives $n$ = 3.5 for $h_b$ = 30 m and 2.9 for 200 m: between free space and plane earth, reflecting diffraction and clutter.
- Egli is plane earth plus $20\log(f/40)$: at 433 MHz that is +20.7 dB over plane earth, representing average terrain/clutter excess loss in its 1950s US dataset.
- Log-distance is the generic fit: measure $L$ at many points, regress against $\log d$; the slope gives $n$, the residual RMS gives σ.
- The distributions of **shadowing** (lognormal, from obstruction by terrain/buildings over many wavelengths) and **fast fading** (Rayleigh/Rician, from multipath within a few wavelengths) are separate and multiply ([multipath-fading-doppler](multipath-fading-doppler.md), [link-margin-availability](link-margin-availability.md)).

### Level 3 — the ITU-R/NTIA methods and where secondary sources disagree
| Method | Scope | Inputs | Use for Marcus |
|---|---|---|---|
| ITU-R P.528-4 (2019) [1] | aeronautical/air–ground; 125–15 500 MHz; heights 1.5 m–20 km AMSL; $q$ = 1–99 % | distance, both heights, $f$, time % | rocket in flight at < 20 km (curved-earth two-ray + diffraction + troposcatter; isotropic antennas) |
| ITM / Longley–Rice (NTIA) [2] | 20 MHz–20 GHz, > 1 km; free space + diffraction + troposcatter; area or point-to-point mode | terrain profile (or Δh), heights, ground constants, climate, reliability/confidence | landed rocket behind terrain, ground-level links over hills |
| ITU-R P.1812 [3] | 30 MHz–6 GHz; 0.25–3000 km; terminals ≲ 3 km above ground; 1–50 % time, 1–99 % locations | terrain + clutter profile | same as ITM, ITU-flavoured; includes clutter and ducting |
| ITU-R P.1546 [4] | point-to-area, 30–4000 MHz, 1–1000 km, 1–50 % time | effective height, distance, curves | coverage-style estimates, not path-specific |
| ITU-R P.1411 [6] | short range outdoor (≲ 1 km), 300 MHz–100 GHz, street canyons, below/above rooftop | geometry, environment class | urban ground-level LoRa / campus links |
| ITU-R P.452 [7] | interference between stations on the Earth's surface (~0.1–50 GHz), incl. ducting and troposcatter | profile, climate | co-channel interference between teams/ground stations over long paths |
| ITU-R P.2108 / P.2109 | clutter loss / building entry loss | environment | add to above for terminals in clutter/indoors |

Open-source implementations exist: NTIA publishes ITM and P.528 (C++/Python wrappers on GitHub, github.com/NTIA); community MATLAB/Python implementations of P.1546/P.1812 (e.g. github.com/eeveetza) are available. The KB's `prop_empirical.py` only implements the closed-form models.

**Contradictions in secondary sources (recorded in the research log):**
- *Egli constants.* The ratio form above gives 88.0 dB (isotropic) in dB form; widely copied dB versions use 85.9 − 20 log $h_m$ or 83.9 − 20 log $h_m$ for $h_m \ge$ 10 m, and 76.3 − 10 log $h_m$ below 10 m. 83.9 ≈ 88.0 − 4.3 (two dipole gains of 2.15 dB), suggesting some versions assume dipole-referenced gains; 85.9 gives continuity (±0.4 dB) with the 76.3 branch at 10 m. **Use the ratio form with explicit antenna gains.**
- *Okumura–Hata.* Frequency validity quoted as 150–1000 MHz (e.g. Stüber's lecture notes [10]) or 150–1500 MHz (Hata/Rappaport); the large-city constant appears as 8.28 or 8.29; the open-area term appears with 18.33 (Rappaport, Hata) or 19.33 (Stüber) — the latter changes open-area loss by $\log f$ ≈ 2.6–3 dB at UHF. This page uses 18.33 and 8.29.
- *Antenna reference.* Hata formulas give median basic transmission loss; whether they already include antenna gains relative to dipoles is inconsistently stated. Treat them as isotropic-to-isotropic loss and budget gains separately, noting ±2 dB uncertainty.

## Design equations & rules of thumb

| Model | Use when | Don't use when |
|---|---|---|
| Free space | elevated paths with clear first Fresnel zone | either terminal near the ground beyond $d_c$ |
| Plane earth / two-ray | flat open ground, clear LOS, $d > 4h_1h_2/\lambda$ | hills, trees in path, $d$ beyond horizon |
| Log-distance + σ | you have measurements to fit $n$, σ | extrapolating far beyond the fitted range |
| Okumura–Hata | 150–1500 MHz, base 30–200 m, mobile 1–10 m, 1–20 km, urban/suburban/open | low base antennas (LoRa nodes at 2 m), air-to-ground |
| COST-231–Hata | 1500–2000 MHz cellular | below 1500 MHz |
| Egli | quick VHF/UHF irregular-terrain estimate | anything needing better than ±10 dB |
| P.528 | aircraft/rocket/balloon to ground | ground-to-ground |
| ITM / P.1812 | terrain-specific ground paths | inside cities without clutter data |
| P.1411 | < 1 km urban/suburban | long rural paths |

Typical path-loss exponents: free space 2; open flat ground beyond breakpoint ~4; suburban 2.7–3.5; urban 3–5; in-building obstructed 4–6 (Rappaport Table 4.2 [11]).

## Worked examples
**1 — Same geometry, different models (base 30 m, mobile 1.5 m).** From `prop_empirical.py`:

| d (km) | FSPL 433 | Plane earth | Hata urban 433 | Hata suburban 433 | Hata open 433 | Egli (ratio) 433 |
|---|---|---|---|---|---|---|
| 1 | 85.2 | 86.9 | 118.1 | 109.9 | 92.3 | 107.6 |
| 5 | 99.2 | 114.9 | 142.7 | 134.5 | 116.9 | 135.6 |
| 10 | 105.2 | 126.9 | 153.3 | 145.1 | 127.5 | 147.6 |
| 20 | 111.2 | 139.0 | 164.0 | 155.7 | 138.1 | 159.7 |

At 915 MHz the Hata figures are 6–10 dB higher (urban 5 km: 151.2 dB). Hata-open tracks plane earth within ~2 dB here — it is essentially the plane-earth regime for this geometry — while urban clutter adds ~28 dB. (Plane earth is *below* FSPL at 1 km for 915 MHz because 1 km is barely past the 0.55 km breakpoint; there the exact two-ray result should be used.)

**2 — Two LoRa nodes at 2 m, 3 km apart, 915 MHz.** Hata returns 152 dB but is **invalid** ($h_b$ = 2 m ≪ 30 m). Plane earth gives 127 dB (FSPL 101 dB). With 14–22 dBm handheld nodes, 0–2 dBi antennas and SF12 (−137 dBm) the plane-earth budget gives about +24 to +36 dB of margin in open flat country — consistent with community reports of several-km ground-level ranges — while any real obstruction (trees, a building, terrain) can remove that margin quickly.

**3 — Rocket in flight at 3 km altitude, 30 km ground range.** Elevation 5.6°; path well clear of terrain near the GS ⇒ free space (114.7 dB at 433 MHz, 121.2 dB at 915 MHz over the ≈ 30 km slant path) with lobing from ground reflection; P.528 at 50 % time would return approximately free space plus small corrections for this geometry, and its 1–10 % values quantify the fading (not computed here).

**4 — Fitting your own log-distance model.** Walk/drive test with the ground-station receiver logging RSSI vs GPS distance from a transmitter at the planned recovery-beacon height; regress $L = L_0 + 10n\log d$; typical results for flat scrub: $n$ ≈ 3.5–4.5, σ ≈ 5–8 dB. Use the fitted $n$ and σ in the landed-rocket budget with a margin for 90–95 % location reliability ([link-margin-availability](link-margin-availability.md)).

*Selection bias — log the packets nobody heard (W5-S11, 2026-10-13; `tools/verify/sim2_coverage_itm.py`, [tool landscape Example 5](../16-simulation-tools/tool-landscape-overview.md)).* If the data set holds only the packets that arrived (a TTN-Mapper-style survey, or your own receiver log without the transmitter's log), the fit is biased toward the lucky tail of the fading. A simulation of 4 000 attempts at 0.2–20 km with true $n$ = 3.5, σ = 8 dB, 14 dBm EIRP and a −120 dBm threshold: only 20 % arrive, none beyond 5 km. Ordinary least squares on the received points gives **$n$ = 1.70**, σ = 6.1 dB and a median range of 1.17 km instead of 0.48 km (**+142 %**). A censored (Tobit) maximum-likelihood fit that also uses the positions of the failed attempts gives $n$ = 3.60, σ = 8.06 dB, 0.47 km. A truncated fit (received points plus the known threshold only) gave $n$ = 4.32 — better than OLS but poorly pinned. **An exponent below 2 from a field survey is a symptom of censoring, not evidence of better-than-free-space propagation.** So log every transmission with its position and time on the transmitter side, mark which ones were received, and fit the censored model.

## Practical notes
- **Terrain data:** SRTM 1-arcsecond (~30 m) DEMs are free; add canopy height. Tools: Radio Mobile (ITM), SPLAT! (ITM), QGIS plugins, NTIA's ITM library, pyITM ports.
- **Model disagreement is information:** if free space and plane earth differ by 30 dB for your link, your link lives in the regime where antenna height dominates — test it rather than trusting either.
- **For launch campaigns,** do an ITM/P.1812 run from each planned ground-station site to the predicted landing ellipse to find **shadows** (ridges between the station and the ellipse) and choose the site that avoids them. Do not take ITM's extra margin for a landed antenna at face value: on a real 15 km profile it gave 10–50 dB less loss than flat-earth two-ray at 0.5 m ([tool landscape Example 4](../16-simulation-tools/tool-landscape-overview.md)); budget with the two-ray number ([two-ray](two-ray-ground-reflection.md#worked-examples)) and measure.

## Common mistakes & misconceptions
- **Using Okumura–Hata for low antennas, air-to-ground, or outside 150–1500 MHz.**
- **Believing a "LoRa range calculator"** without knowing its model — many silently apply Hata or free space.
- **Comparing models with different antenna references** (dipole vs isotropic, gains included or not).
- **Extrapolating a log-distance fit** from 1 km data to 30 km (the regime changes).
- **Fitting $n$ to received-only (mapper) data.** The failures are missing, so the fit gives a low exponent (1.7 for a true 3.5 in the KB's simulation) and overstates range 2–3× — fit a censored model with the failed attempts included (Example 4).
- **Treating the median prediction as the design value** — the ITU-R methods give time/location percentiles; design with the appropriate percentile.

## How to simulate / verify
- `tools/verify/prop_empirical.py` — FSPL, plane earth, Hata (urban/suburban/open, validity flags), COST-231, Egli (ratio and quoted forms, constant check), log-distance.
- `tools/verify/prop_two_ray.py`, `prop_knife_edge.py` — physical models for ground-level and obstructed paths.
- **ITM is now in `tools/rfcalc`** (port of NTIA's public-domain C++, verified against NTIA's area/p2p test vectors within 0.05 dB; `tools/rfcalc/tests/test_itm.py`): `cd tools && python3 -m rfcalc itm --f 433.92M --d 10km --dh 30 --htx 5 --hrx 0.5 --pol 0` (area mode), or add `--profile elev.txt --spacing 150.7` for point-to-point with an equally spaced elevation file (TX end first). Defaults: climate 1 (equatorial), N₀ 360, εr 15, σ 0.005 S/m. P.528 is not wrapped yet.
- `tools/verify/sim2_coverage_itm.py` — ITM vs two-ray on a real SRTM profile, and the censored-data fit (OLS vs Tobit vs truncated).

## Open questions / gaps
- ITM has been run (2026-10-13) for one example site (Spaceport America plain, SRTM-90), not for the team's own launch sites; P.528 and P.1812 are still not implemented, and no DEM tile loader is automated. Which of ITM and two-ray is right for a landed antenna is unmeasured.
- Hata's original paper was not re-read; the formula here follows Rappaport and Stüber, and the listed discrepancies stand.
- P.1411 and P.452 were described from their scopes only.

## Sources
1. ITU-R Recommendation P.528-4 (08/2019), *A propagation prediction method for aeronautical mobile and radionavigation services using the VHF, UHF and SHF bands* — scope: 125 MHz–15.5 GHz, heights 1.5 m–20 km, time 1–99 %. https://www.itu.int/rec/R-REC-P.528/en (standard)
2. NTIA/ITS, *Irregular Terrain Model (ITM) (Longley–Rice) (20 MHz – 20 GHz)*, https://its.ntia.gov/software/itm/ and https://github.com/NTIA/itm; A. G. Longley, P. L. Rice, "Prediction of tropospheric radio transmission loss over irregular terrain: a computer method," ESSA Tech. Rep. ERL 79-ITS 67 (1968). (standard/technical report)
3. ITU-R Recommendation P.1812-7 (08/2023)/-8 (09/2025), *A path-specific propagation prediction method for point-to-area terrestrial services in the frequency range 30 MHz to 6 GHz* (0.25–3000 km; 1–50 % time; 1–99 % locations). https://www.itu.int/rec/R-REC-P.1812 (standard)
4. ITU-R Recommendation P.1546-6 (08/2019), *Method for point-to-area predictions for terrestrial services in the frequency range 30 MHz to 4 000 MHz* (1–1000 km; 1–50 % time). https://www.itu.int/rec/R-REC-P.1546 (standard)
5. M. Hata, "Empirical formula for propagation loss in land mobile radio services," *IEEE Trans. Veh. Technol.* VT-29(3), 317–325 (1980); Y. Okumura et al., "Field strength and its variability in VHF and UHF land-mobile radio service," *Rev. Elec. Commun. Lab.* 16, 825–873 (1968). (peer-reviewed) *cited via textbooks*
6. ITU-R Recommendation P.1411, *Propagation data and prediction methods for the planning of short-range outdoor radiocommunication systems* (300 MHz–100 GHz). https://www.itu.int/rec/R-REC-P.1411 (standard) *scope only*
7. ITU-R Recommendation P.452, *Prediction procedure for the evaluation of interference between stations on the surface of the Earth*. https://www.itu.int/rec/R-REC-P.452 (standard) *scope only*
8. COST Action 231, *Digital mobile radio towards future generation systems — final report*, European Commission, 1999, ch. 4. (technical report)
9. J. J. Egli, "Radio propagation above 40 MC over irregular terrain," *Proc. IRE* 45(10), 1383–1391 (1957); ratio form as given in Wikipedia "Egli model". (peer-reviewed / encyclopedia)
10. G. L. Stüber, EE6604 *Personal & Mobile Communications*, Week 7 "Path loss models, shadowing," Georgia Tech, 2019. https://wireless-systems.ece.gatech.edu/6604/2019-lectures/week7.pdf (lecture notes)
11. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, §4.9–4.10 (log-distance, lognormal shadowing, Okumura, Hata, COST-231, Table 4.2 exponents). (textbook)
12. Meshtastic, "Range tests" (community records). https://meshtastic.org/docs/overview/range-tests/ (community — anecdotal)
13. `tools/verify/prop_empirical.py` (this KB).
