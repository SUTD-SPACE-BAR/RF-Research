---
title: Ground-wave and LF/MF propagation — Sommerfeld–Norton surface wave, ITU-R P.368, ground conductivity, MF broadcast and why HF ground wave dies quickly
domain: 09-propagation-link-budget
slug: ground-wave-and-lf-mf-propagation
tags: [ground-wave, surface-wave, Sommerfeld, Norton, numerical-distance, attenuation-function, ITU-R-P.368, ITU-R-P.527, ITU-R-P.832, LFMF, GRWAVE, ground-conductivity, vertical-polarization, MF-broadcast, LF, VLF, Millington, mixed-path, HF-surface-wave-radar, NDB, time-signals]
prerequisites: [two-ray-ground-reflection.md, friis-free-space-path-loss.md, ../02-electromagnetics/boundary-conditions-reflection-refraction.md]
related: [hf-propagation-modes-and-prediction.md, ionospheric-hf-propagation.md, fresnel-zones-los-radio-horizon.md, diffraction-knife-edge.md, ../08-antennas/dipoles-and-monopoles.md, ../08-antennas/antenna-simulation-nec-openems.md, ../02-electromagnetics/skin-effect-conductor-loss-roughness.md]
level: mixed
confidence: high
last_updated: 2026-10-03
---

# Ground-wave and LF/MF propagation — Sommerfeld–Norton surface wave, ITU-R P.368, ground conductivity, MF broadcast and why HF ground wave dies quickly

## Questions this page answers
- What is the ground wave (surface wave), and how is it different from line-of-sight and skywave?
- Why does ground-wave range shrink as frequency rises, and why is HF ground wave limited to tens of km over land?
- Why does ground wave need vertical polarisation?
- How much do sea water, wet ground and dry ground change coverage?
- How do I compute ground-wave field strength (ITU-R P.368, Norton's numerical distance, LFMF/GRWAVE)?
- Why can I hear far-away AM (MW) stations only at night, and why do they fade?
- What happens on a mixed land–sea path (Millington method, recovery effect)?
- What are LF/VLF used for (time signals, navigation, submarines), and why do they reach so far?
- Does ground wave help my landed rocket's 433 MHz beacon? (No — and why.)

## TL;DR
- **Ground wave = the space wave (direct + ground-reflected) + the Norton surface wave** guided along the Earth–air boundary. With both antennas near the ground, the direct and reflected waves cancel (Γ ≈ −1 at grazing incidence), leaving the surface wave. Its strength is the inverse-distance field times an **attenuation function $|A(p)|$** of **Norton's numerical distance** $p \approx \dfrac{\pi d}{\lambda}\dfrac{|\eta - 1|}{|\eta|^2}$, where $\eta = \varepsilon_r - jx$ and $x = \sigma/(\omega\varepsilon_0) = 1.8\times10^4\,\sigma/f_\text{MHz}$.
- **Over good ground, |p| grows ∝ f²/σ.** At 30 km over 3 mS/m land, |p| ≈ 5.8 at 1 MHz and ≈ 139 at 10 MHz (`tools/verify/prop2_ground_wave.py` §3). Once |p| ≫ 1, $A \to 1/(2p)$ and the field falls as **1/d²** instead of 1/d. Beyond the diffraction distance (≈ 80/f^{1/3} km) the curved Earth adds an exponential decay. **Higher frequency ⇒ much shorter range**, the reason HF ground wave dies within ~15–40 km over land.
- **Vertical polarisation only.** For horizontal polarisation $p_h \approx (\pi d/\lambda)|\eta|$, thousands of times larger. Over land at 1 MHz the H-pol ground wave is **60–73 dB weaker** than V-pol at 1–30 km (script §4). Hence MF/LF masts are vertical monopoles over buried radial ground systems.
- **Conductivity is everything.** Ranges to 40 dB(µV/m) for 1 kW from a short monopole, computed with P.368's integral method:

| Ground | 200 kHz | 1 MHz | 7 MHz |
|---|---|---|---|
| Sea (5 S/m) | 860 km | 608 km | 338 km |
| Wet ground (10 mS/m) | 709 km | 160 km | 28 km |
| Land (3 mS/m) | 472 km | 90 km | 22 km |
| Medium-dry ground (1 mS/m) | 272 km | 58 km | 18 km |

- **Validated method:** the script is an independent Python re-implementation of NTIA's LFMF, the software that ITU-R P.368-10 makes integral to the Recommendation. It uses a flat-earth Norton function with curvature corrections below 80/f^{1/3} km and the Wait–Fock residue series beyond. It reproduces all five LFMF reference cases (to 0.05 dB), and the two methods join within 0.03 dB at the switch distance.
- **MF day/night:** by day the D layer absorbs MF skywave, so AM coverage is pure ground wave (tens to hundreds of km). At night the skywave returns, giving distant reception, co-channel interference and a **fading zone** where ground wave and skywave are comparable.
- **For Marcus:** at 433/915 MHz the Norton surface wave is negligible beyond a few wavelengths (|p| ≈ 200 at 1 km over 3 mS/m land at 433 MHz, so A ≈ −52 dB). A landed rocket's link is governed by the two-ray/plane-earth model and minimum effective antenna height ([two-ray](two-ray-ground-reflection.md)), not by ground wave.

## Intuition (no math)
A vertical antenna standing on the ground launches a wave whose electric field points up and down. Where that wave touches the ground, it drives currents in the soil or sea. If the ground were a perfect conductor, the wave would glide along it with no loss, falling only as 1/distance like any spreading wave. Real ground is a lossy conductor. The wave's "foot" dragging through it loses energy, and the wavefront tilts forward and bleeds energy downward into the ground. The worse the conductor, and the higher the frequency (more cycles, more loss per metre), the faster the wave dies.

Sea water (5 S/m) is close to a perfect conductor at LF/MF, so ground wave over the sea goes hundreds of km. Dry sand at 10 MHz is hopeless: tens of km. A horizontally polarised wave has its electric field parallel to the ground, where the ground nearly shorts it out. It cannot be guided at all.

Two more effects shape real coverage. The Earth is round, so beyond a certain distance the wave must diffract around the bulge, which makes higher frequencies die faster still. And at night the ionosphere becomes a second path for MF (skywave), bringing in distant stations and interfering with the local ground wave.

## The math

### Level 1 — the working formulas
- **Reference field** (P.368): a short vertical monopole on a perfect ground plane radiating 1 kW produces 300 mV/m at 1 km (cymomotive force 300 V). So $E_0 = 300/d_\text{km}$ mV/m, or $E_0 = 109.5 - 20\log d_\text{km}$ dB(µV/m).
- **Ground-wave field** (flat Earth): $E = E_0\,|A(p)|\,\times$(height-gain factors).
- **Complex relative permittivity**: $\eta = \varepsilon_r - jx$, with $x = \sigma/(\omega\varepsilon_0) = 17\,975\,\sigma/f_\text{MHz}$.
- **Numerical distance** (vertical polarisation): $p = -j\frac{kd}{2}\frac{\eta - 1}{\eta^2}$, so $|p| \approx \frac{\pi d}{\lambda}\frac{|\eta - 1|}{|\eta|^2}$. For $x \gg \varepsilon_r$ this becomes $|p| \approx \pi d/(\lambda x)$, which grows as $f^2/\sigma$. For horizontal polarisation $p_h = -j\frac{kd}{2}(\eta - 1)$.
- **Attenuation function** (Sommerfeld–Norton, exact flat-earth form): $A(p) = 1 - j\sqrt{\pi p}\,e^{-p}\operatorname{erfc}(j\sqrt p)$, i.e. $A = 1 + j\sqrt\pi\,q_iw(q_i)$ with $q_i^2 = p$ and $w$ the Faddeeva function. Bullington's real-argument approximation: $A \approx \frac{2 + 0.3p}{2 + p + 0.6p^2}$. Limits: $A \to 1$ ($p \ll 1$) and $A \to 1/(2p)$ ($p \gg 1$, so $E \propto 1/d^2$).
- **Basic transmission loss from field strength** (P.368): $L_b = 142.0 + 20\log f_\text{MHz} - E_\text{dB(µV/m)}$ dB.
- **Spherical Earth** (beyond ≈ $80/f_\text{MHz}^{1/3}$ km): the Wait–Fock residue series
$$\frac{E}{E_0} = \sqrt{\pi x_e}\,\Big|\sum_s \frac{e^{-jx_et_s}}{t_s - q^2}\Big|,\qquad x_e = \nu\frac{d}{a_e},\ \nu = \Big(\frac{a_ek}{2}\Big)^{1/3},\ q = -j\nu\delta,\ \delta = \frac{\sqrt{\eta - 1}}{\eta}.$$
  - The $t_s$ are the roots of $w_1'(t) - q\,w_1(t) = 0$, with $w_1(t) \propto \mathrm{Ai}(t\,e^{-j2\pi/3})$.
  - The effective radius is $a_e = a_0/(1 - 0.04665\,e^{0.005577N_s})$ (LFMF convention).

### Level 2 — where it comes from and what it means
**Sommerfeld's problem.** A vertical Hertzian dipole sits above a homogeneous lossy half-space. The exact field is a Sommerfeld integral. Norton evaluated it asymptotically for the case where both antennas are near the surface and the distance is many wavelengths. The total field splits into the geometric-optics space wave (direct + image weighted by the Fresnel coefficient $\Gamma_V$) plus a **surface-wave term** $(1 - \Gamma_V)A(p)$. At grazing incidence $\Gamma_V \to -1$, the space wave cancels, and $(1 - \Gamma_V) \to 2$. The ground-level field is then $2\times$(free-space field of the dipole) × $A(p)$, which is the same as $E_0A$ with $E_0$ the perfect-ground field. **There is no separate "Zenneck wave" to launch**: the Norton term is part of the radiated field, falling off as the attenuation function dictates.

**Why the numerical distance scales as f²/σ.** The surface impedance seen by a grazing vertically polarised wave is $Z_s/\eta_0 = \sqrt{\eta - 1}/\eta \approx 1/\sqrt{\eta}$. Loss accumulates as $k\,d\,|Z_s/\eta_0|^2/2$. With $|\eta| \approx x \propto \sigma/f$, this gives $p \approx kd/(2x) \propto f\cdot f/\sigma$. Over land (3 mS/m) at 30 km the script finds $|p|$ = 1.4 (0.5 MHz), 5.4 (1 MHz), 32 (3 MHz), 133 (10 MHz) and 408 (30 MHz). At 10 MHz $x$ = 5.4 is no longer ≫ $\varepsilon_r$ = 22, and $|p|$ then grows more slowly than f²: ×24 from 1 to 10 MHz instead of ×100. In Bullington's approximation that means −17 dB at 1 MHz but −48 dB at 10 MHz at the same 30 km. Over the sea, $x$ ≈ 9000 at 10 MHz and $|p|$ is only 0.35 at 30 km. **This is the physics of "maximum ground-wave range decreases with frequency".**

Numerical distance at 30 km and Bullington's attenuation (script §3):

| f (MHz) | ground | x = σ/(ωε₀) | \|p\| at 30 km | A (dB) |
|---|---|---|---|---|
| 0.5 | 1 mS/m | 36 | 4.0 | −13.8 |
| 0.5 | 3 mS/m | 108 | 1.43 | −5.6 |
| 1 | 1 mS/m | 18 | 13.1 | −26.0 |
| 1 | 3 mS/m | 54 | 5.4 | −16.7 |
| 1 | sea | 89 900 | 0.0035 | 0.0 |
| 3 | 3 mS/m | 18 | 32 | −35.0 |
| 10 | 3 mS/m | 5.4 | 133 | −48.2 |
| 10 | sea | 8 990 | 0.35 | −1.2 |
| 30 | 3 mS/m | 1.8 | 408 | −58.1 |
| 30 | sea | 3 000 | 3.2 | −11.5 |

**Why vertical polarisation.** For horizontal polarisation the relevant factor is $\sqrt{\eta - 1}$ instead of $\sqrt{\eta - 1}/\eta$. Then $|p_h| \approx (\pi d/\lambda)|\eta|$, larger by $|\eta|^2$ (10³–10¹⁰). A horizontal antenna near the ground is also shorted by its image. The script's full calculation over land at 1 MHz gives H − V = −60 dB at 1 km and −73 dB at 30 km.

| Distance (1 MHz, land 3 mS/m) | 1 km | 3 km | 10 km | 30 km |
|---|---|---|---|---|
| Vertical pol (dBµV/m) | 107.7 | 96.1 | 80.5 | 61.6 |
| Horizontal pol (dBµV/m) | 47.8 | 28.8 | 7.8 | −11.6 |
| H − V (dB) | −59.8 | −67.3 | −72.7 | −73.1 |

**From flat to round Earth.** Beyond ~80/f^{1/3} km (80 km at 1 MHz, 37 km at 10 MHz, 137 km at 200 kHz) the field must diffract around the bulge. The residue series takes over, and each term decays as $\exp(x_e\,\Im t_s)$. The first root dominates far out, giving an exponential loss in dB/km that grows as $f^{1/3}$ even over perfect ground, and much faster over poor ground. The script's two methods agree to ≤ 0.03 dB at the switch point for land, sea and dry ground (§1b), a strong internal consistency check. For elevated antennas, height-gain functions $w_1(t - y)/w_1(t)$ with $y = kh/\nu$ multiply each term. P.368 notes the method stays valid up to $h \approx 1.2\sigma^{1/2}\lambda^{3/2}$ when $\varepsilon_r \ll 60\lambda\sigma$.

### Level 3 — real paths
- **Mixed paths (Millington, P.368 Annex 2).** For sections $S_1, S_2, \dots$ the field is the average of the "forward" and "reverse" constructions:
  - $E_R = E_1(d_1) - E_2(d_1) + E_2(d_1 + d_2)$;
  - $E_T = E_2(d_2) - E_1(d_2) + E_1(d_1 + d_2)$;
  - result $E = (E_R + E_T)/2$, which is reciprocal.

  Example (script §6), 1 MHz, 50 km land then 50 km sea: all-land 37.9, all-sea 68.5, mixed **53.2 dB(µV/m)**. The field *rises* after the coastline (the **recovery effect**), which is why coastal MW reception is better than inland.
- **Seasonal and local variability.** P.368 quotes lognormal location variability σ ≈ 3–4 dB (≈ 3.5 dB). It also quotes 5–15 dB winter/summer differences at 500–1000 kHz in cold climates (frozen ground) and 10–20 dB at 150–280 kHz over 1000–2000 km.
- **Ground-constant data.** P.527 gives the electrical characteristics of soils, water and ice vs frequency. P.832 is the world atlas of ground conductivity below 1 MHz; national maps such as the FCC M3 map are also used. The P.368 curve set uses: sea (5 S/m, εr 70; 1 S/m, εr 80 for low salinity), wet ground (10 mS/m, εr 30), land (3 mS/m, εr 22), medium-dry ground (1 mS/m, εr 15), plus fresh water and ice.
- **LF/VLF.** Below ~300 kHz the ground wave reaches hundreds to thousands of km. The **Earth–ionosphere waveguide** (D/E-region "ceiling" at 70–90 km) carries VLF (3–30 kHz) around the globe with ~2–3 dB per 1000 km. Uses:
  - submarine communication: VLF penetrates a few metres of sea water;
  - time signals: JJY 40/60 kHz, BPC 68.5 kHz, WWVB 60 kHz, DCF77 77.5 kHz, MSF 60 kHz;
  - Loran-C/eLoran navigation at 100 kHz, whose ground-wave phase is corrected for "additional secondary factor" (conductivity-dependent delay);
  - NDBs: 190–535 kHz.
- **Why VLF goes round the world (waveguide view).** Between the conducting ground and the D/E-region "ceiling" at height $h$ ≈ 70 km (day) to 90 km (night), the guide behaves like a parallel-plate waveguide. Its TM₀ (TEM-like) mode has no cut-off. The higher modes TEₙ/TMₙ cut off at $f_n = nc/(2h)$ ≈ 1.7–2.1 kHz for n = 1, so only a few modes propagate at 10–30 kHz. Attenuation is a few dB per 1000 km, and the day/night change of $h$ shifts the received phase, which is used to monitor the D region.
- **MF broadcasting.** The 526.5–1606.5 kHz band (9 kHz channels in ITU Regions 1 and 3; 10 kHz in Region 2) is planned around ground-wave service areas by day. Night-time skywave protection is handled separately with ITU-R P.1147.
- **HF ground wave in practice.** Over land, HF ground wave serves only local links of ~10–40 km. Over the sea it supports **HF surface-wave radar** (3–30 MHz, ~200 km for current mapping, ship detection), maritime MF/HF distress (2182 kHz) and coastal stations. NVIS is used instead of ground wave for regional HF over land ([HF modes](hf-propagation-modes-and-prediction.md)).

## Design equations & rules of thumb

| Quantity | Formula / value | Notes |
|---|---|---|
| Reference field | 300 mV/m at 1 km for 1 kW (109.5 − 20 log d dBµV/m) | short monopole, perfect ground |
| Ground loss parameter | x = 1.8×10⁴ σ / f_MHz | sea x ≫ εr up to HF; land x ≈ εr near 10 MHz |
| Numerical distance (V) | ≈ π d /(λ x) for x ≫ εr | ∝ f²/σ |
| Attenuation | A ≈ (2 + 0.3p)/(2 + p + 0.6p²) | p ≫ 1: A ≈ 1/(2p), E ∝ 1/d² |
| Flat/round switch | d ≈ 80 / f_MHz^(1/3) km | 80 km at 1 MHz |
| Basic loss | L_b = 142.0 + 20 log f_MHz − E | P.368 |
| H vs V | H-pol 60–70 dB weaker over land at MF | use vertical radiators |
| 40 dBµV/m range, 1 kW, land 3 mS/m | 472 km (0.2 MHz), 90 km (1 MHz), 22 km (7 MHz), 15 km (14 MHz) | script §5 |
| Same, sea water | 860 / 608 / 338 / 209 km | |
| Location variability | σ ≈ 3.5 dB lognormal | P.368 note 2 |
| Mixed path | Millington average of forward and reverse | recovery effect at the coast |

## Worked examples
**1 — A 1 kW MW broadcaster at 1 MHz: coverage by ground type.** From script §2 (dB(µV/m), ground-level antennas):

| Path | 10 km | 30 km | 100 km | 300 km |
|---|---|---|---|---|
| Sea | 89.5 | 79.8 | 68.5 | 54.9 |
| Land 3 mS/m | 80.5 | 61.6 | 37.9 | 11.2 |
| Medium dry | 72.1 | 52.2 | 29.4 | 2.6 |

With a primary-service target of ≈ 60 dB(µV/m) (1 mV/m), coverage is ≈ 30 km over typical land and ≈ 250 km over sea. The same transmitter on a coastal site beaming over water covers several times the area. At night the skywave adds distant reception and interference.

**1b — The full frequency picture** (script §2; 1 kW short monopole, both antennas at ground level, vertical polarisation, dB(µV/m); the inverse-distance field is 89.5 / 80.0 / 69.5 / 60.0 / 49.5 at 10 / 30 / 100 / 300 / 1000 km):

| f | Ground | 10 km | 30 km | 100 km | 300 km | 1000 km |
|---|---|---|---|---|---|---|
| 0.2 MHz | sea | 89.5 | 79.9 | 69.1 | 57.7 | 36.2 |
| 0.2 MHz | land 3 mS/m | 89.1 | 78.8 | 65.8 | 49.5 | 16.6 |
| 3 MHz | sea | 89.4 | 79.6 | 67.5 | 51.0 | 7.2 |
| 3 MHz | land 3 mS/m | 63.4 | 43.6 | 20.0 | −12.6 | −105.8 |
| 10 MHz | sea | 89.0 | 78.2 | 62.8 | 36.8 | −40.5 |
| 10 MHz | land 3 mS/m | 50.5 | 30.6 | 4.7 | −39.1 | −177.8 |
| 30 MHz | sea | 85.4 | 68.4 | 39.3 | −13.1 | −183.4 |
| 30 MHz | land 3 mS/m | 40.5 | 20.1 | −9.7 | −70.0 | −269.3 |

Read across a row to see the 1/d → 1/d² → exponential transition. Read down a column to see the frequency law: at 100 km over land the field falls from 65.8 (0.2 MHz) to 20.0 (3 MHz), 4.7 (10 MHz) and −9.7 dB(µV/m) (30 MHz). Over sea at 0.2 MHz the field stays within 1 dB of inverse distance out to 100 km.

**2 — Why a 7 MHz "local" net over Singapore land uses NVIS, not ground wave.** Over 3 mS/m land at 7 MHz, 1 kW reaches 40 dB(µV/m) at only ≈ 22 km. At 100 W (−10 dB) the 30 dB(µV/m) contour is still only ~20–25 km away, roughly the size of the island. Short HF skywave (NVIS) on 5–7 MHz covers 0–400 km evenly.

**3 — Field strength to received power and SNR at MF.** 40 dB(µV/m) at 1 MHz into an isotropic antenna gives $P_r = E - 20\log f - 107.2$ = 40 − 0 − 107.2 = −67.2 dBW = −37.2 dBm. Man-made noise in a residential area at 1 MHz is $F_a$ = 72.5 dB above $kT_0b$. In 9 kHz: −174 + 39.5 + 72.5 = −62 dBm. That gives an SNR of +25 dB for an *isotropic* antenna. A real ferrite-rod receive antenna has an efficiency of −30…−40 dBi, but it loses signal and noise alike, since external noise dominates at MF. This is why MW is "noise-limited", not sensitivity-limited ([HF noise](hf-propagation-modes-and-prediction.md#level-1--definitions-and-formulas-with-units)).

**4 — The landed rocket at 433 MHz.** Over land (εr 15, σ 1 mS/m), $x$ = 1.8×10⁴ × 0.001/433 = 0.04 ≪ εr, so $\eta \approx 15$. At 1 km, $|p| \approx (\pi\cdot1000/0.69)(14/225)$ ≈ 280, so $A \approx 1/(2p)$ ≈ −55 dB. The surface wave is negligible. What matters is the two-ray interference of the direct and reflected waves and the *minimum effective height* (≈ 44 cm for V-pol at 433 MHz over medium ground). Lifting either antenna is the fix ([two-ray worked examples](two-ray-ground-reflection.md#worked-examples)).

**5 — HF surface-wave radar over the sea.** At 10 MHz over sea water the one-way ground-wave field at 100 km is 62.8 dB(µV/m), only 6.7 dB below inverse distance. At 300 km it is 36.8 dB(µV/m), 23 dB below. A monostatic radar suffers this loss twice. That is why coastal HF ocean radars (current mapping, ship detection) reach ~100–200 km at 5–25 MHz, and why the same frequencies reach only tens of km over land.

**6 — Coastal mixed path at 1 MHz.** A transmitter 50 km inland, then 50 km of sea to a ship: 53.2 dB(µV/m) (Millington). That is 15 dB better than an all-land path of the same length and 15 dB worse than all sea.

## Practical notes
- **Antenna and ground system.** An MF/LF vertical's efficiency depends on its ground system. Classic broadcast practice is 120 buried λ/4 radials; ground losses fall roughly as 1/N for the first few tens of radials ([dipoles and monopoles](../08-antennas/dipoles-and-monopoles.md)). Elevated radials and counterpoises are the compact alternatives. Top-loading improves radiation resistance for electrically short masts.
- **Measuring.** Field-strength surveys along radials from the transmitter, fitted to P.368 curves, are the classic way to measure *effective* ground conductivity, which is why ITU/FCC conductivity maps exist.
- **Software.** NTIA **LFMF** is the P.368-10 integral software; it is open source and this KB re-implements it. **GRWAVE** is the older ITU program behind the P.368 curves, with an exponential atmosphere and elevated antennas to 10 GHz. NEC-2/4 with a Sommerfeld ground computes near-field and ground-wave fields of arbitrary antennas ([NEC/openEMS](../08-antennas/antenna-simulation-nec-openems.md)).
- **Amateur LF/MF:** 2200 m (135.7–137.8 kHz) and 630 m (472–479 kHz), with tight EIRP limits (1 W and 5 W EIRP in many administrations). Ground wave plus night skywave; WSPR and JT9 are the common modes. Check local IMDA rules ([licensing](../19-regulations-safety/amateur-radio-licensing.md)).

### Quick answers to common exam-style questions
- *How does maximum ground-wave range change when frequency increases?* It decreases: the numerical distance grows ≈ f²/σ, and Earth diffraction loss also grows with f.
- *What polarisation does ground wave support?* Vertical (H-pol is 60–70 dB weaker over land at MF).
- *Why is AM reception of distant stations a night-time phenomenon?* The daytime D layer absorbs MF skywave. At night the skywave returns, while the ground wave is unchanged.
- *Which surface gives the longest ground-wave range?* Sea water (σ ≈ 5 S/m), then wet ground, then dry ground, sand and rock.

## Common mistakes & misconceptions
- **"Ground wave follows the ground, so it should work at any frequency."** Its attenuation grows roughly as f²/σ. At VHF/UHF it is irrelevant beyond a few wavelengths, and line-of-sight plus diffraction take over.
- **"A horizontal dipole close to the ground is a good ground-wave antenna."** The H-pol surface wave is tens of dB weaker; use vertical radiators.
- **"Only the soil near the transmitter matters."** The whole path matters (Millington). A coastline part-way along raises the field (the recovery effect), and dry inland sections suppress it.
- **"The surface wave is a separate Zenneck wave you can launch for long-distance low-loss transmission."** Over real ground the Norton surface-wave term of an ordinary radiator is what P.368 computes. There is no extra, low-loss mode to exploit.
- **"MW reception is worse at night because of noise."** At night the *skywave* returns. It brings distant stations, co-channel interference and fading where skywave and ground wave are comparable. The local ground wave itself is unchanged.
- **Using free-space or Friis loss for LF/MF ground-wave links.** That underestimates loss by tens of dB over poor ground. Use P.368/LFMF.

## How to simulate / verify
- `tools/verify/prop2_ground_wave.py` (ALL PASS, 17 checks; output `prop2_ground_wave_output.txt`) covers:
  - an independent re-implementation of NTIA LFMF (P.368-10): flat-earth Norton function via the Faddeeva function plus curvature terms, and the Wait residue series with Airy-function roots found by Newton and continuation;
  - validation against the 5 LFMF reference cases;
  - flat/residue continuity;
  - field-strength tables for 0.2–30 MHz over sea, wet, land and dry ground;
  - Norton numerical distance and Bullington's approximation;
  - V vs H polarisation;
  - coverage distances;
  - a Millington mixed path.
- Cross-check: NEC-2 (PyNEC) with Sommerfeld–Norton ground and `RP` surface-wave output, for a short vertical over the same ground constants.

## Open questions / gaps
- The P.368 published curve values (figures) were not digitised, so the comparison is with LFMF's reference cases and with internal consistency. The very-dry-ground and ice categories of P.368-9 were not confirmed (secondary sources disagree: 0.1 mS/m, εr 3 vs 0.3 mS/m, εr 7), so they are omitted.
- No Singapore-specific ground-conductivity values were extracted from P.832; 3 mS/m is a generic land value.
- Night-time MF skywave field strength (ITU-R P.1147) is not computed.

## Sources
1. ITU-R Recommendation P.368-10 (08/2022), *Ground-wave propagation prediction method for frequencies between 10 kHz and 30 MHz* — conditions, 300 mV/m reference, Lb = 142.0 + 20 log f − E, variability notes, near-field correction, Millington mixed-path method (Annex 2); integral software = LFMF. https://www.itu.int/rec/R-REC-P.368/en (standard)
2. ITU-R Recommendation P.368-7 (03/1992) — ground-wave curves computed with GRWAVE; curve ground constants (e.g. wet ground 10 mS/m, εr 30). (standard, superseded)
3. NTIA/ITS, *LFMF — Low Frequency / Medium Frequency propagation model* (C++), https://github.com/NTIA/LFMF, and test data https://github.com/NTIA/LFMF-test-data (LFMF_Examples.csv) — algorithm (flat-earth curve correction, Wait residue series, DeMinco surface impedance) and reference results. (reference software, US government)
4. ITU-R Recommendation P.527-6 (09/2021), *Electrical characteristics of the surface of the Earth* (Attachment: legacy εr/σ curves used by P.368/P.832); ITU-R P.832-4 (07/2015), *World Atlas of Ground Conductivities*. https://www.itu.int/rec/R-REC-P.527/en (standards)
5. K. A. Norton, "The propagation of radio waves over the surface of the earth and in the upper atmosphere," *Proc. IRE* 24(10), 1367–1387 (1936) and 25(9), 1203–1236 (1937); A. Sommerfeld, *Ann. Phys.* 28, 665 (1909). (peer-reviewed) *cited from standard knowledge*
6. K. Bullington, "Radio propagation fundamentals," *Bell Syst. Tech. J.* 36(3), 593–626 (1957) — surface-wave attenuation approximation and charts. https://archive.org/details/bstj36-3-593 (peer-reviewed)
7. J. R. Wait, *Electromagnetic Waves in Stratified Media*, Pergamon 1962 / IEEE Press 1996 — residue series, Airy functions w1, height-gain. (textbook) *cited via [3]*
8. R. J. King, "Electromagnetic wave propagation over a constant impedance plane," *Radio Science* 4, 255–268 (1969); G. Millington, "Ground-wave propagation over an inhomogeneous smooth earth," *Proc. IEE* 96(III), 53–64 (1949). (peer-reviewed) *cited from standard knowledge / via [1]*
9. J. D. Parsons, *The Mobile Radio Propagation Channel*, 2nd ed., Wiley 2000, ch. 2 (surface wave); S. R. Saunders, A. Aragón-Zavala, *Antennas and Propagation for Wireless Communication Systems*, 2nd ed., Wiley 2007. (textbooks)
10. ARRL, *The ARRL Antenna Book* — ground systems and radials for verticals, MF/LF amateur practice. (handbook) *cited from standard knowledge*
11. `tools/verify/prop2_ground_wave.py` (this KB).
