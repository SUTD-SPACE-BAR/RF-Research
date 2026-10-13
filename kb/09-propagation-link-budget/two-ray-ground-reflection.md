---
title: Two-ray ground reflection, plane-earth loss and antenna-height effects
domain: 09-propagation-link-budget
slug: two-ray-ground-reflection
tags: [two-ray, ground-reflection, plane-earth, breakpoint-distance, 40-dB-per-decade, Fresnel-reflection-coefficient, Brewster-angle, lobing, minimum-effective-antenna-height, rough-surface, landed-rocket]
prerequisites: [friis-free-space-path-loss.md, fresnel-zones-los-radio-horizon.md, ../02-electromagnetics/boundary-conditions-reflection-refraction.md]
related: [empirical-path-loss-models.md, multipath-fading-doppler.md, diffraction-knife-edge.md, polarization-mismatch-loss.md, link-budget-methodology.md, ../08-antennas/antennas-on-rockets.md, ../15-lora-ism-radios/ground-station-design.md]
level: mixed
confidence: high
last_updated: 2026-10-14
---

# Two-ray ground reflection, plane-earth loss and antenna-height effects

## Questions this page answers
- Why does path loss near the ground grow at 40 dB per decade instead of 20?
- What is the breakpoint (critical) distance, and why does raising an antenna help so much?
- Why does the signal from a climbing rocket fade in and out every few seconds at the ground station?
- Does polarisation matter for ground reflection? What is the Brewster angle?
- Why is a landed rocket so hard to hear, and does it matter which way it is lying?
- What is the "minimum effective antenna height"?
- How rough does the ground have to be before the reflection stops mattering?

## TL;DR
- Two paths reach the receiver: direct and ground-reflected. Their path difference is $\Delta \approx 2h_1h_2/d$ and the reflection coefficient is ≈ −1 at grazing, so the field is $E \approx E_0\,|1 - e^{-jk\Delta}| = 2E_0\,|\sin(2\pi h_1h_2/\lambda d)|$.
- **Beyond the breakpoint $d_c = 4h_1h_2/\lambda$** the loss (isotropic antennas) becomes the **plane-earth law** $L = 40\log_{10}d - 20\log_{10}(h_1h_2)$ dB ($d$, $h$ in m) — independent of frequency, 40 dB/decade (verified: 40.00 dB/decade, `tools/verify/prop_two_ray.py`). Doubling either antenna height buys 6 dB.
- Below the breakpoint the two rays interfere, producing deep nulls and peaks (lobing) around the free-space value.
- **Ground-station lobing:** with a mast of height $h$, nulls occur at elevations $\sin\theta_n \approx n\lambda/2h$: 433 MHz, 5 m → 0°, 4.0°, 8.0°, 12.0°…; a rocket climbing at 300 m/s at 20 km range crosses a null every ~8 s. **Vertical polarisation lobes are shallow** (3–9 dB peak-to-null between 5° and 30° over medium ground, Brewster dip at 14.5°); horizontal polarisation lobes are deep (18–33 dB).
- **Minimum effective height:** at grazing incidence a real ground makes an antenna behave as if it were at least $h_0 = \lambda/(2\pi|z|)$ high: at 433 MHz over medium-dry ground **h₀ ≈ 44 cm for vertical, 3 cm for horizontal polarisation** — vertical antennas near the ground work much better.
- **Landed rocket** (antenna 0.1 m up, horizontal, 5 m GS mast): two-ray loss at 5 km = 153.6 dB vs FSPL 99.2 dB (**+54 dB**); at 433 MHz with the E22, margin +14 dB at 2.4 kb/s at 5 km, +2 dB at 10 km. A vertical whip 0.3 m up is **≈ 14 dB better**. On a **real terrain profile**, NTIA's ITM (`rfcalc itm`) gives **10–50 dB less loss** than this flat-earth model for a landed antenna — and cannot run below 0.5 m at all — so the two-ray number is the pessimistic planning bound, not a prediction ([tool landscape Example 4](../16-simulation-tools/tool-landscape-overview.md)).

## Intuition (no math)
Over flat ground a receiver hears the transmitter twice: directly, and via a mirror image of the transmitter reflected in the ground. At grazing angles almost all the energy reflects, and the reflection flips the sign of the field. When the two paths are nearly the same length — which happens far away, where both rays are almost horizontal — the flipped reflection nearly *cancels* the direct wave. The farther you go, the closer the path lengths, the better the cancellation: the residual field falls much faster than $1/d$. Raising either antenna increases the path difference and reduces the cancellation, which is why antenna height is worth more than transmit power for ground-level links.

Closer in, the path difference can be half a wavelength, a whole wavelength, and so on: then the rays alternately reinforce (up to +6 dB) and cancel (deep nulls). As a rocket climbs, the elevation angle at the ground station sweeps through these peaks and nulls — the ground station hears slow, periodic fades.

Polarisation matters because the ground reflects the two polarisations differently. Horizontally polarised waves are reflected almost completely at low angles. Vertically polarised waves have a **Brewster angle** (≈ 10–15° over typical soils) where the reflection almost vanishes — so a vertically polarised link suffers much shallower lobing at moderate elevations. At grazing, both polarisations reflect strongly, but the details of *how* the reflection approaches −1 make vertical antennas close to the ground behave as if they were half a metre higher than they are, while horizontal ones get no such help.

## The math

### Level 1 — the model and its limits
- Geometry (flat earth): antenna heights $h_1, h_2$, ground distance $d$. Direct path $r_d = \sqrt{d^2 + (h_1-h_2)^2}$; reflected $r_r = \sqrt{d^2 + (h_1+h_2)^2}$; grazing angle $\psi = \arctan((h_1+h_2)/d)$.
- Field ratio (isotropic antennas): $\dfrac{E}{E_0} = 1 + \Gamma(\psi)\dfrac{r_d}{r_r}e^{-jk(r_r - r_d)}$, $k = 2\pi/\lambda$.
- Path difference $\Delta = r_r - r_d \approx 2h_1h_2/d$ for $d \gg h$.
- Received power: $P_r = P_tG_tG_r\left(\dfrac{\lambda}{4\pi r_d}\right)^2\left|\dfrac{E}{E_0}\right|^2$.
- Breakpoint: $d_c = 4h_1h_2/\lambda$ (phase difference $k\Delta = \pi$: the last maximum).
- Plane-earth loss ($d \gg d_c$, $\Gamma \to -1$): $P_r = P_tG_tG_r\dfrac{h_1^2h_2^2}{d^4}$; $L = 40\log_{10}d - 20\log_{10}(h_1h_2)$ dB.

### Level 2 — derivation
With $\Gamma = -1$ and $r_d \approx r_r$: $|E/E_0| = |1 - e^{-jk\Delta}| = 2|\sin(k\Delta/2)| = 2\left|\sin\dfrac{2\pi h_1h_2}{\lambda d}\right|$.
- For $d \ll d_c$: the argument is large; $|E/E_0|$ oscillates between 0 and 2 (nulls and +6 dB peaks).
- For $d \gg d_c$: $\sin x \approx x$ ⇒ $|E/E_0| \approx \dfrac{4\pi h_1h_2}{\lambda d}$. Multiply the free-space power $(\lambda/4\pi d)^2$ by $(4\pi h_1h_2/\lambda d)^2$: $\lambda$ cancels and $P_r/P_t = G_tG_r(h_1h_2)^2/d^4$.
The script compares the exact two-ray model (complex Fresnel coefficients, exact path lengths) with the plane-earth formula: at 433 MHz, $h_1$ = 2 m, $h_2$ = 5 m ($d_c$ = 57.8 m): 100.0 vs 100.0 dB at 1 km, 128.0 vs 128.0 dB at 5 km, 152.0 vs 152.0 dB at 20 km; the slope from 10 to 100 km is 40.00 dB/decade.

**Fresnel reflection coefficients** (grazing angle $\psi$, complex relative permittivity $\varepsilon_c = \varepsilon_r - j\sigma/(\omega\varepsilon_0) = \varepsilon_r - j60\sigma\lambda$):
$$\Gamma_H = \frac{\sin\psi - \sqrt{\varepsilon_c - \cos^2\psi}}{\sin\psi + \sqrt{\varepsilon_c - \cos^2\psi}},\qquad \Gamma_V = \frac{\varepsilon_c\sin\psi - \sqrt{\varepsilon_c - \cos^2\psi}}{\varepsilon_c\sin\psi + \sqrt{\varepsilon_c - \cos^2\psi}}.$$
(H = E-field parallel to the ground, TE; V = E-field in the plane of incidence, TM. Some texts use the opposite sign convention for $\Gamma_V$; with this one both tend to −1 at grazing.) Derived in [02-electromagnetics/boundary-conditions-reflection-refraction](../02-electromagnetics/boundary-conditions-reflection-refraction.md).
- **Brewster (pseudo-Brewster) angle** for V: $|\Gamma_V|$ is minimum at $\psi_B \approx \arctan(1/\sqrt{\varepsilon_r})$ for low-loss ground: 30.0° (very dry, $\varepsilon_r$ = 3), 14.5° (medium dry, 15), 10.4° (wet, 30). Over sea water (lossy) it becomes 3.9° at 433 MHz and 5.2° at 915 MHz with $|\Gamma_V|_\text{min}$ ≈ 0.32/0.24 (script §2).
- Ground constants used: ITU-R P.527 legacy categories — very dry 3/10⁻⁴ S/m, medium dry 15/10⁻³, wet 30/10⁻², sea 70/5 S/m [3] (typical values only; real soils vary with moisture).

### Level 3 — minimum effective height, lobing, roughness, curvature
**Minimum effective antenna height.** Expand the coefficients for small $\psi$ with $z_H = \sqrt{\varepsilon_c-1}$, $z_V = \sqrt{\varepsilon_c-1}/\varepsilon_c$: $\Gamma \approx -1 + 2\psi/z$. Then $1 + \Gamma e^{-jk\Delta} \approx jk\Delta + 2\psi/z$, and with $\psi \approx (h_1+h_2)/d$ and $\Delta = 2h_1h_2/d$, for one low antenna ($h_1 \ll h_2$):
$$\left|\frac{E}{E_0}\right| \approx \frac{2kh_2}{d}\left|h_1 - \frac{j}{kz}\right| \;\Rightarrow\; h_{1,\text{eff}} = \left|h_1 - \frac{j}{kz}\right|,\quad h_0 = \frac{\lambda}{2\pi|z|}.$$
This is the analytical content behind Bullington's "minimum effective antenna height" chart [4]. Values (script §3): 433 MHz — H: 2.9 cm (medium dry), 2.1 cm (wet), 0.7 cm (sea); V: 44 cm, 61 cm, 163 cm. 915 MHz — H: 1.4/1.0/0.5 cm; V: 21/29/57 cm. The effective-height formula matches the exact two-ray model within 0.3 dB (e.g. V-pol, $h_1$ = 0.1 m, $h_2$ = 5 m, 5 km: 140.7 dB exact, 140.8 dB formula, 154.0 dB naive plane-earth). (At very low heights and MF/HF frequencies the Norton surface wave also matters; at UHF over km distances its contribution is captured by this expansion.)

**Elevation lobing at a ground station.** For a distant target at elevation $\theta$ and a receive antenna at height $h$, the reflected ray's extra path is $2h\sin\theta$. With $\Gamma \approx -1$, nulls occur where $2h\sin\theta = n\lambda$: $\sin\theta_n = n\lambda/(2h)$ (including $\theta = 0$) and peaks at $(n+\tfrac12)\lambda/2h$. The lobing *depth* depends on $|\Gamma(\theta)|$: peak-to-null $= 20\log_{10}\frac{1+|\Gamma|}{1-|\Gamma|}$ (for isotropic patterns). Over medium-dry ground at 433 MHz (script §7):

| Elevation | $|\Gamma_H|$ | H peak-to-null | $|\Gamma_V|$ | V peak-to-null |
|---|---|---|---|---|
| 1° | 0.991 | 46.6 dB | 0.869 | 23.1 dB |
| 5° | 0.954 | 32.7 dB | 0.482 | 9.1 dB |
| 10° | 0.911 | 26.7 dB | 0.180 | 3.2 dB |
| 14.5° | 0.875 | 23.5 dB | 0.001 | 0.0 dB |
| 30° | 0.766 | 17.6 dB | 0.330 | 6.0 dB |
| 60° | 0.632 | 12.9 dB | 0.544 | 10.6 dB |

A directional ground antenna pointed up at the rocket illuminates the ground less (its pattern toward the reflection point is reduced), shrinking the lobing further. The **fade rate** for a target climbing at vertical speed $v_z$ at range $R$: $f_\text{lobe} = \frac{2h\cos\theta}{\lambda}\dot\theta$ with $\dot\theta \approx v_z\cos\theta/R$ — 0.13 Hz (a null every 7.9 s) for 300 m/s at 20 km, 10° elevation, $h$ = 3 m; 0.38 Hz for 500 m/s at 10 km, 20° (script §4). These are slow, deterministic fades: packets sent during a null are lost regardless of SF.

**Circular polarisation and reflection.** A perfect conductor has (in this convention) $\Gamma_H = -1$, $\Gamma_V = +1$: the relative sign of the two components flips and a reflected circularly polarised wave comes back with the **opposite hand** (the familiar "a mirror reverses handedness"). Over real ground, $\Gamma_V$ has that conductor-like positive sign only **above the Brewster angle**; below it, $\Gamma_V$ becomes negative like $\Gamma_H$. So above $\psi_B$ a reflected RHCP wave arrives mostly LHCP (rejected by an RHCP antenna), while below $\psi_B$ it arrives mostly RHCP but elliptical (since $|\Gamma_V| < |\Gamma_H|$) and is *not* rejected. This is the same reasoning used for GNSS multipath (low-elevation reflections are the dangerous ones). For a CP ground station tracking a rocket at 10–60° elevation over medium ground ($\psi_B$ ≈ 14.5°), much of the ground reflection is cross-polar and suppressed; at very low elevations during final descent it is not.

**Rough ground.** Specular reflection is reduced by the Ament factor $\rho_s = \exp[-8(\pi\sigma_h\sin\psi/\lambda)^2]$ ($\sigma_h$ = RMS height variation). At 433 MHz: $\sigma_h$ = 0.3 m reduces the specular reflection to 0.98 at 2°, 0.64 at 10°, 0.03 at 30° (script §8). So at grazing angles (landed rocket, ground-level links) even rough ground reflects strongly and the 40 dB/decade law holds; at the elevations of an ascending rocket, rough terrain or vegetation largely kills the reflection (the Rayleigh criterion $\sigma_h < \lambda/(8\sin\psi)$ gives the "smooth" limit).

**Curved earth.** Over long paths, the reflection point moves, the grazing angle is computed on the $4/3$-earth, and a divergence factor $D < 1$ reduces the reflected ray; beyond the radio horizon diffraction takes over (ITU-R P.526 §3). ITU-R P.528 implements a curved-earth two-ray model for air-to-ground links from 125 MHz to 15.5 GHz [5].

## Design equations & rules of thumb

| Equation | When valid | Typical values |
|---|---|---|
| $d_c = 4h_1h_2/\lambda$ | flat earth | 433 MHz, 2 m & 5 m: 58 m; 30 m & 1.5 m: 260 m |
| $L = 40\log d - 20\log(h_1h_2)$ | $d \gg d_c$, grazing | 2 m & 5 m: 100 dB @1 km, 128 dB @5 km |
| +6 dB per doubling of either height | plane-earth regime | |
| $h_\text{eff} = \sqrt{h^2 + h_0^2}$-ish, $h_0 = \lambda/2\pi|z|$ | low antenna, grazing | 433 MHz medium ground: V 0.44 m, H 0.03 m |
| $\sin\theta_n = n\lambda/2h$ | GS lobing nulls | 433 MHz, 3 m: 6.6°, 13.3°… |
| $\psi_B \approx \arctan(1/\sqrt{\varepsilon_r})$ | V pol, low-loss ground | 10–30° |
| $\rho_s = e^{-8(\pi\sigma_h\sin\psi/\lambda)^2}$ | rough surface | smooth if $\sigma_h < \lambda/(8\sin\psi)$ |

## Worked examples
**1 — Landed rocket at 433 MHz (5 m GS mast, medium-dry ground).** Two-ray loss (script §5):

| Distance | 1 km | 2 km | 5 km | 10 km | 20 km |
|---|---|---|---|---|---|
| H-pol, antenna 0.1 m up (dipole along a horizontal body) | 125.7 | 137.7 | 153.6 | 165.6 | 177.7 dB |
| V-pol, whip 0.3 m up | 111.3 | 123.3 | 139.1 | 151.1 | 163.2 dB |
| FSPL | 85.2 | 91.2 | 99.2 | 105.2 | 111.2 dB |

Budget (33 dBm, 0 dBi, 11 dBic GS, −3 dB CP, −1 dB feeder): H-pol $P_r$ = −97.7 dBm (2 km), −113.6 (5 km), −125.6 (10 km), −137.7 (20 km): against −128 dBm (2.4 kb/s) the link fails between 10 and 20 km; at SF12 (−137 dBm) it reaches ~20 km. The V-pol whip gives +14.4 dB throughout. (This is the licensed 2 W case. At Singapore's licence-exempt 10 mW e.r.p. subtract 20.35 dB: −118.1 dBm at 2 km, −134.0 dBm at 5 km — 2.4 kb/s fails beyond ≈ 3.5 km and SF12 beyond ≈ 6 km; see [19 Singapore rules](../19-regulations-safety/singapore-imda-rules.md).) Also note that a horizontal dipole has a pattern null *along the body axis*: if the rocket lies pointing at the ground station, even the H-pol numbers are optimistic ([polarization-mismatch-loss](polarization-mismatch-loss.md) — landing cases).

*Against a terrain model (W5-S11, 2026-10-13; `tools/verify/sim2_coverage_itm.py`, [tool landscape Example 4](../16-simulation-tools/tool-landscape-overview.md)).* The same case was run through the KB's port of NTIA's Irregular Terrain Model (verified against NTIA's test vectors within 0.05 dB) on a real 14.9 km SRTM-90 profile (the Spaceport America plain, an example site). ITM rejects the 0.1 m height (error 1001, minimum 0.5 m, warns below 1 m), so the rocket antenna was raised to 0.5 m. Basic transmission loss at 433.92 MHz, H-pol:

| d | two-ray 0.1 m (as above, at the profile's distances) | two-ray 0.5 m | ITM, flat profile, 0.5 m | ITM, real profile, 0.5 m |
|---|---|---|---|---|
| 1.06 km | 126.6 | 113.0 | 112.3 | 109.5 dB |
| 4.97 km | 153.5 | 139.9 | 141.0 | 122.8 dB |
| 9.95 km | 165.6 | 151.9 | 156.2 | 109.3 dB |
| 14.92 km | 172.6 | 159.0 | 164.6 | 111.9 dB |

On a flat profile ITM agrees with two-ray (+0.1 to +5.6 dB). On the real, concave profile it is up to **≈ 50 dB more optimistic**, because ITM measures antenna heights above a straight line fitted through the terrain, which puts both ends tens of metres "up" and removes the ground-reflection cancellation. Mirroring the profile to put a 160 m hump in the path still left ITM ≈ 10 dB below flat. So **two defensible models differ by 10–50 dB** for a landed antenna; this is model-form uncertainty, not an error in either. The KB's recommendation: plan recovery with this flat-earth two-ray at the real antenna height, use a terrain tool only to find ridges and shadows between the station and the landing zone, and measure (beacon at known points, log every packet). The canonical landed-rocket set ([00 canonical values](../00-math-foundations/canonical-values-and-conventions.md)) keeps the two-ray number for that reason.

**2 — Rocket on the pad.** Vertical antenna 3 m up on the rail, GS at 5 m, V-pol: 96.6 dB at 1 km (FSPL 85.2 dB; +11 dB), 124.3 dB at 5 km (+25 dB). Pad checks at 1–2 km are therefore a poor predictor of flight performance (the flight link is nearly free space and much better) and an OK predictor of the landed case.

**3 — Choosing the GS mast height for ascent tracking.** At 433 MHz a 3 m mast puts lobing nulls at 6.6° and 13.3°; a 10 m mast at 2.0°, 4.0°, 6.0°… (denser, narrower nulls). With a V-pol or CP antenna the nulls above ~5° are shallow; the lowest null (at the horizon) is unavoidable and deepens as the rocket descends. For the final descent, height matters more than lobing: a higher mast raises the plane-earth signal by 20 log(h) and extends the horizon.

**4 — Ground-level LoRa sanity check.** Two nodes at 2 m, 3 km apart, 915 MHz: plane-earth 127.0 dB vs FSPL 101.2 dB — 26 dB worse (`prop_empirical.py`). This explains the gulf between LoRa "record" ranges (elevated) and typical ground-level results.

## Practical notes
- **Measure the ground you have:** a quick check is to compare RSSI at two mast heights on a known path; a 6 dB change per height doubling confirms the plane-earth regime.
- **For recovery beacons,** a vertical monopole with a small ground plane that ends up vertical after landing (or a deployable whip) exploits the V-pol minimum effective height; a horizontal dipole lying in grass is close to the worst case.
- **Water and wet ground** increase $|\Gamma_V|$ at low angles and raise V-pol $h_0$ (163 cm over sea at 433 MHz): coastal and over-water landings behave differently from dry fields.
- **Pad/field tests:** raise the rocket-side antenna to a representative height or test with a drone-lifted transmitter; otherwise the test measures ground reflection, not the flight link.

## Common mistakes & misconceptions
- **Using FSPL for ground-level links** (tens of dB optimistic beyond the breakpoint).
- **Believing plane-earth loss is frequency-independent in practice** — it is for isotropic antennas and heights above $h_0$; with real low antennas (V-pol $h_0 \propto \lambda$) and fixed-size antennas, frequency matters again.
- **Assuming polarisation is irrelevant near the ground** — H vs V differs by ~14 dB for a 0.1–0.3 m high antenna at 433 MHz, and lobing depth differs by 20 dB.
- **Interpreting slow periodic fades as interference or a bad cable** — for an ascending rocket they are usually ground-reflection lobing.
- **Using the Fresnel coefficient with the wrong angle** (incidence from normal vs grazing angle from the surface).

## How to simulate / verify
- `tools/verify/prop_two_ray.py` — exact two-ray loss with complex Fresnel coefficients (H/V), breakpoint and 40 dB/decade check, pseudo-Brewster angles, minimum effective height (formula vs exact), GS null elevations and lobing rate, landed-rocket and pad tables, lobing depth vs elevation, Ament roughness factor.
- NEC-2/4 models of the actual antennas over real ground (Sommerfeld–Norton ground) give pattern × ground reflection directly ([08-antennas/antenna-simulation-nec-openems](../08-antennas/antenna-simulation-nec-openems.md)).
- ITU-R P.528 (NTIA open-source implementation) for curved-earth air-to-ground predictions including the two-ray region ([empirical-path-loss-models](empirical-path-loss-models.md)); not yet wrapped in `tools/`.
- Terrain: `cd tools && python3 -m rfcalc itm --f 433.92M --d 10km --dh 30 --htx 5 --hrx 0.5 --pol 0` (ITM area mode), or `--profile elev.txt --spacing 150.7` for a point-to-point terrain profile (port of NTIA ITM, tests in `tools/rfcalc/tests/test_itm.py`). Heights must be ≥ 0.5 m; below 1 m ITM warns that it is outside its recommended range.

## Open questions / gaps
- Soil constants at the actual launch/landing sites are assumed from ITU-R P.527 legacy categories; P.527-6's moisture-based soil model could be implemented for better values.
- Near-ground antenna impedance and pattern changes (a dipole lying on the ground detunes) are not modelled here — NEC needed (domain 08).
- Which of two-ray and ITM is closer for a landed rocket on real terrain (they differ by 10–50 dB) is unmeasured; a beacon walk with every transmission logged would settle it for a given site.

## Sources
1. T. S. Rappaport, *Wireless Communications*, 2nd ed., 2002, §4.6 (two-ray ground reflection model, $d_c$, $d^{-4}$ law). (textbook)
2. A. Goldsmith, *Wireless Communications*, Cambridge UP 2005, §2.4 (two-ray model, critical distance $4h_th_r/\lambda$). (textbook)
3. ITU-R Recommendation P.527-6 (09/2021), *Electrical characteristics of the surface of the Earth*, Attachment Fig. 24 (legacy P.527-3 ground categories). https://www.itu.int/rec/R-REC-P.527/en (standard)
4. K. Bullington, "Radio propagation fundamentals," *Bell Syst. Tech. J.* 36(3), 593–626 (1957) — plane-earth formula, surface wave, minimum effective antenna height chart. https://archive.org/details/bstj36-3-593 (peer-reviewed)
5. ITU-R Recommendation P.528-4 (08/2019), *A propagation prediction method for aeronautical mobile and radionavigation services using the VHF, UHF and SHF bands*. https://www.itu.int/rec/R-REC-P.528/en (standard)
6. W. S. Ament, "Toward a theory of reflection by a rough surface," *Proc. IRE* 41(1), 142–146 (1953). (peer-reviewed) — specular reduction factor.
7. J. D. Parsons, *The Mobile Radio Propagation Channel*, 2nd ed., Wiley 2000, ch. 2 (plane earth, surface wave, roughness). (textbook)
8. `tools/verify/prop_two_ray.py`, `tools/verify/prop_empirical.py` (this KB).
